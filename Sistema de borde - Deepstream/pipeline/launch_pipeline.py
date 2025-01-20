#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2021-2023 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
################################################################################

"""
This script processes RTSP video streams, detects objects using a specified inference engine, 
and saves frames with detected objects. It sets up a GStreamer pipeline and configures various 
GStreamer elements like source bins, inference plugins, video converters, and sinks.

Main functionalities include:
- Creating and linking GStreamer elements for processing video streams.
- Handling buffers and frames to check for detected objects.
- Saving detected frames and sending alerts when specific objects are detected.

Attributes:
    MUXER_BATCH_TIMEOUT_USEC (int): The timeout value for batch formation in the muxer element.
"""

import sys
from common.bus_call import bus_call
from common.platform_info import PlatformInfo
import pyds
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import datetime
import time
import numpy as np
import cv2
from get_rtsp import make_requests
from utils import send_alert, should_send_alert

from monitoring.logging_handler.logger import logger

MUXER_BATCH_TIMEOUT_USEC = 33000
CODEC = "H264"
BITRATE = 2000000
GIE = "nvinfer"
TS_FROM_RTSP = False
CONFIDENCE_BIAS = 0.6
SEEK_CLASS = 0
STREAMMUX_WIDTH = 1920
STREAMMUX_HEIGHT = 1080

# Variable global para almacenar los FPS de cada cámara
fps_streams = {}

def on_new_sample(sink):
    """
    Callback function to process a new sample from the GStreamer sink.

    This function is called whenever a new buffer is pulled from the sink. It processes the 
    buffer to check for detected objects and extracts frames. If a person is detected, it saves 
    the frame as an image and sends an alert.

    Args:
        sink (Gst.Element): The sink element from which the sample is pulled.

    Returns:
        Gst.FlowReturn: Status of the sample processing (OK or ERROR).
    """
    global fps_streams  # Para modificar la variable global

    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR

    buffer = sample.get_buffer()
    if not buffer:
        logger.error("Error al obtener el buffer")
        return Gst.FlowReturn.ERROR

    try:
        # Obtener metadatos del batch
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))
        l_frame = batch_meta.frame_meta_list

        while l_frame is not None:
            try:
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            frame_number = frame_meta.frame_num
            camera_id = frame_meta.pad_index

            # Actualizar contador de frames y tiempo para el cálculo de FPS
            if camera_id not in fps_streams:
                # Inicializar datos para el nuevo flujo
                fps_streams[camera_id] = {
                    'frame_count': 0,
                    'start_time': time.time(),
                    'last_time': time.time(),
                    'fps': 0
                }

            fps_data = fps_streams[camera_id]
            fps_data['frame_count'] += 1
            current_time = time.time()
            elapsed_time = current_time - fps_data['last_time']

            # Calcular FPS cada segundo
            if elapsed_time >= 1.0:
                fps = fps_data['frame_count'] / elapsed_time
                fps_data['fps'] = fps
                logger.info(f"Flujo {camera_id}: {fps:.2f} FPS")
                # Reiniciar contador y tiempo
                fps_data['frame_count'] = 0
                fps_data['last_time'] = current_time

            # Obtener la superficie del buffer (frame)
            surface = pyds.get_nvds_buf_surface(hash(buffer), frame_meta.batch_id)
            if surface is None:
                logger.error("Error: Surface is not accessible")
                return Gst.FlowReturn.ERROR

            # Convertir la superficie a un array de NumPy (RGBA)
            frame_array = np.array(surface, copy=True, order='C')
            frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_RGBA2BGR)

            # Indicador para saber si se detectó una persona
            person_detected = False

            # Iterar sobre los objetos detectados en el frame
            l_obj = frame_meta.obj_meta_list
            while l_obj is not None:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break

                # Si se detecta una persona
                if obj_meta.class_id == SEEK_CLASS and obj_meta.confidence >= CONFIDENCE_BIAS:
                    person_detected = True  # Se detectó al menos una persona

                    # Obtener las coordenadas de la caja
                    rect_params = obj_meta.rect_params
                    top = int(rect_params.top)
                    left = int(rect_params.left)
                    width = int(rect_params.width)
                    height = int(rect_params.height)

                    # Dibujar la caja en el frame
                    cv2.rectangle(frame_rgb, (left, top), (left + width, top + height), (0, 0, 255), 2)

                    # Obtener la etiqueta del objeto directamente
                    obj_label = obj_meta.obj_label
                    confidence = obj_meta.confidence
                    label_text = f"{obj_label} {confidence:.2f}"

                    # Poner la etiqueta en el frame
                    cv2.putText(frame_rgb, label_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break

            # Después de procesar todos los objetos, verificar si se detectó alguna persona
            if person_detected:
                if should_send_alert(camera_id):
                    logger.info(f"Persona(s) detectada(s) en la cámara {camera_id}, frame {frame_number}")

                    # Guardar la imagen
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = f"out/frame_appsink_{frame_number}_{timestamp}.jpg"
                    cv2.imwrite(image_path, frame_rgb)
                    logger.info(f"Frame guardado desde appsink como: {image_path}")

                    # Preparar y enviar alerta
                    result = {
                        'camera_id': camera_id,
                        'timestamp': timestamp,
                        'frame': frame_rgb
                    }
                    # print(result)
                    send_alert(result)
                else:
                    logger.info(f"Alarma en cámara {camera_id} no enviada. No han pasado 2 minutos desde el último envío.")

            try:
                l_frame = l_frame.next
            except StopIteration:
                break

    except RuntimeError as e:
        logger.error(f"Error al extraer la superficie del buffer: {e}")

    return Gst.FlowReturn.OK

def cb_newpad(decodebin, decoder_src_pad, data):
    """
    Callback function for handling new pads added to decodebin elements.

    This function links the decoder's source pad to a source bin's ghost pad if the new pad 
    is for video content and uses the NVIDIA memory type.

    Args:
        decodebin (Gst.Element): The decodebin element.
        decoder_src_pad (Gst.Pad): The newly created source pad of the decoder.
        data (Gst.Bin): The source bin to link with the decoder source pad.
    """
    logger.info("In cb_newpad\n")
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)

    # Check if the new pad is for video (not audio)
    logger.info("gstname=", gstname)
    if gstname.find("video") != -1:
        # Link the decodebin pad only if it uses NVIDIA decoder plugin
        logger.info("features=", caps.get_features(0).to_string())
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                logger.error("Failed to link decoder src pad to source bin ghost pad\n")
        else:
            logger.error(" Error: Decodebin did not pick NVIDIA decoder plugin.\n")

def decodebin_child_added(child_proxy, Object, name, user_data):
    """
    Callback function for handling new elements added to decodebin elements.

    Args:
        child_proxy (Gst.Element): The parent element.
        Object (Gst.Element): The child element being added.
        name (str): The name of the child element.
        user_data (Any): User data passed to the callback.
    """
    logger.info("Decodebin child added:", name, "\n")
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)

    if TS_FROM_RTSP:
        if name.find("source") != -1:
            pyds.configure_source_for_ntp_sync(hash(Object))

def create_source_bin(index, uri):
    """
    Create a source bin for a given URI.

    This function creates a GStreamer bin that contains elements for decoding a given URI.

    Args:
        index (int): The index of the source.
        uri (str): The URI to be decoded.

    Returns:
        Gst.Bin: The created source bin.
    """
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the pipeline
    bin_name = f"source-bin-{index}"
    logger.info(bin_name)
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        logger.error(" Unable to create source bin \n")

    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", f"uri-decode-bin-{index}")
    if not uri_decode_bin:
        logger.error(" Unable to create uri decode bin \n")

    # Set the input URI to the source element
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        logger.error(" Failed to add ghost pad in source bin \n")
        return None
    return nbin

def launch_pipeline(camera_codes):
    """
    Main function for setting up and running the GStreamer pipeline.

    This function initializes GStreamer, creates the pipeline, configures elements, and starts 
    processing RTSP streams.

    Args:
        camera_codes (dict): A dictionary of input URIs to process.
    """
    number_sources = len(list(camera_codes.values()))

    cameras = camera_codes

    platform_info = PlatformInfo()
    Gst.init(None)

    logger.info("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        logger.error(" Unable to create Pipeline \n")
    logger.info("Creating streammux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        logger.error(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    for i, uri_name in cameras.items():
        logger.info("Creating source_bin ", i, " \n ")
        source_bin = create_source_bin(i, uri_name)
        if not source_bin:
            logger.error("Unable to create source bin \n")
            continue  # Continue with next source if failed

        # Add a queue for each source
        queue_src = Gst.ElementFactory.make("queue", f"queue_src_{i}")
        if not queue_src:
            logger.error(f"Unable to create queue for source {i} \n")
            continue

        # Configure queue properties
        queue_src.set_property("max-size-buffers", 10)
        queue_src.set_property("leaky", 2)
        queue_src.set_property("silent", True)

        # Add elements to the pipeline
        pipeline.add(source_bin)
        pipeline.add(queue_src)

        # Link source_bin -> queue_src
        srcpad = source_bin.get_static_pad("src")
        sinkpad = queue_src.get_static_pad("sink")
        if srcpad and sinkpad:
            srcpad.link(sinkpad)
        else:
            logger.error(f"Unable to link source_bin to queue_src for source {i} \n")
            continue

        # Link queue_src -> streammux
        sinkpad = streammux.get_request_pad(f"sink_{i}")
        srcpad = queue_src.get_static_pad("src")
        if srcpad and sinkpad:
            srcpad.link(sinkpad)
        else:
            logger.error(f"Unable to link queue_src to streammux for source {i} \n")
            continue

    print("Creating Pgie \n ")
    if GIE == "nvinfer":
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    else:
        pgie = Gst.ElementFactory.make("nvinferserver", "primary-inference")
    if not pgie:
        logger.error(" Unable to create pgie \n")

    logger.info("Creating nvvidconv_to_rgba \n")
    nvvidconv_to_rgba = Gst.ElementFactory.make("nvvideoconvert", "convertor_to_rgba")
    if not nvvidconv_to_rgba:
        logger.error("Error al crear nvvideoconvert para RGBA\n")

    # Create caps filter for RGBA conversion
    caps_rgba = Gst.ElementFactory.make("capsfilter", "filter_rgba")
    if not caps_rgba:
        logger.error("Error al crear capsfilter para RGBA\n")
    caps_rgba.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA"))

    logger.info("Creating nvosd \n ")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        logger.error(" Unable to create nvosd \n")
    nvosd.set_property("process-mode", 0)  # 0 for CPU, 1 for GPU
    nvosd.set_property("display-text", True)

    # Set streammux properties
    streammux.set_property("width", STREAMMUX_WIDTH)
    streammux.set_property("height", STREAMMUX_HEIGHT)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)

    if TS_FROM_RTSP:
        streammux.set_property("attach-sys-ts", 0)

    # Set the configuration file for PGIE
    if GIE == "nvinfer":
        pgie.set_property("config-file-path", "/opt/nvidia/deepstream/deepstream-7.0/sources/deepstream_python_apps/apps/GuardIA-Deepstream-v4/dstest1_pgie_config.txt")
    else:
        pgie.set_property("config-file-path", "/opt/nvidia/deepstream/deepstream-7.0/sources/deepstream_python_apps/apps/GuardIA-Deepstream-v4/dstest1_pgie_inferserver_config.txt")

    pgie_batch_size = pgie.get_property("batch-size")
    if pgie_batch_size != number_sources:
        logger.error(
            "WARNING: Overriding infer-config batch-size",
            pgie_batch_size,
            " with number of sources ",
            number_sources,
            " \n",
        )
        pgie.set_property("batch-size", number_sources)

    appsink = Gst.ElementFactory.make("appsink", "sink")
    if not appsink:
        logger.error("Unable to create appsink\n")

    appsink.set_property("emit-signals", True)
    appsink.set_property("sync", False)
    appsink.connect("new-sample", on_new_sample)

    if not platform_info.is_integrated_gpu():
        logger.info("Configurando nvbuf-memory-type para dGPU")
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        # Set memory type in nvstreammux
        streammux.set_property("nvbuf-memory-type", mem_type)
        # Set memory type in nvvideoconvert
        nvvidconv_to_rgba.set_property("nvbuf-memory-type", mem_type)

    # Create intermediate queue elements
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    queue2 = Gst.ElementFactory.make("queue", "queue2")
    queue3 = Gst.ElementFactory.make("queue", "queue3")
    queue4 = Gst.ElementFactory.make("queue", "queue4")
    queue5 = Gst.ElementFactory.make("queue", "queue5")

    if not queue1 or not queue2 or not queue3 or not queue4 or not queue5:
        logger.error("Unable to create one or more queue elements \n")

    # Configure queue properties
    for queue in [queue1, queue2, queue3, queue4, queue5]:
        queue.set_property("max-size-buffers", 2)
        queue.set_property("leaky", 2)  # Discards old buffers
        queue.set_property("silent", True)

    # Add elements to the pipeline
    pipeline.add(pgie)
    pipeline.add(nvvidconv_to_rgba)
    pipeline.add(caps_rgba)
    pipeline.add(nvosd)
    pipeline.add(appsink)
    pipeline.add(queue1)
    pipeline.add(queue2)
    pipeline.add(queue3)
    pipeline.add(queue4)
    pipeline.add(queue5)

    # Link elements with intermediate queues
    streammux.link(queue1)
    queue1.link(pgie)
    pgie.link(queue2)
    queue2.link(nvvidconv_to_rgba)
    nvvidconv_to_rgba.link(queue3)
    queue3.link(caps_rgba)
    caps_rgba.link(queue4)
    queue4.link(nvosd)
    nvosd.link(queue5)
    queue5.link(appsink)

    # Create an event loop and feed gstreamer bus messages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    # Start playback and listen to events
    logger.info("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except Exception as e:
        logger.error(f"Error no identificado: {e}")
    except BaseException as e:
        logger.error(f"Error al correr el pipeline: {e}")
    except KeyboardInterrupt as e:
        logger.error(f"Interrupción de teclado, finalizando pipeline.")
    finally:
        # Cleanup
        pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    # camera_codes = make_requests()
    camera_codes = {
        0: "rtsp://192.168.1.3:8554/loop1",
        1: "rtsp://192.168.1.3:8554/loop2",
        2: "rtsp://192.168.1.3:8554/loop3",
        3: "rtsp://192.168.1.3:8554/loop4"
    }

    sys.exit(launch_pipeline(camera_codes))
