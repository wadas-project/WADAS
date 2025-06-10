from prometheus_client import start_http_server, Gauge
import os
import sys
import subprocess
import json
import logging

igpu_engines_blitter_0_busy = Gauge(
    "igpu_engines_blitter_0_busy", "Blitter 0 busy utilisation %"
)
igpu_engines_blitter_0_sema = Gauge(
    "igpu_engines_blitter_0_sema", "Blitter 0 sema utilisation %"
)
igpu_engines_blitter_0_wait = Gauge(
    "igpu_engines_blitter_0_wait", "Blitter 0 wait utilisation %"
)

igpu_engines_render_3d_0_busy = Gauge(
    "igpu_engines_render_3d_0_busy", "Render 3D 0 busy utilisation %"
)
igpu_engines_render_3d_0_sema = Gauge(
    "igpu_engines_render_3d_0_sema", "Render 3D 0 sema utilisation %"
)
igpu_engines_render_3d_0_wait = Gauge(
    "igpu_engines_render_3d_0_wait", "Render 3D 0 wait utilisation %"
)

igpu_engines_video_0_busy = Gauge(
    "igpu_engines_video_0_busy", "Video 0 busy utilisation %"
)
igpu_engines_video_0_sema = Gauge(
    "igpu_engines_video_0_sema", "Video 0 sema utilisation %"
)
igpu_engines_video_0_wait = Gauge(
    "igpu_engines_video_0_wait", "Video 0 wait utilisation %"
)

igpu_engines_video_enhance_0_busy = Gauge(
    "igpu_engines_video_enhance_0_busy", "Video Enhance 0 busy utilisation %"
)
igpu_engines_video_enhance_0_sema = Gauge(
    "igpu_engines_video_enhance_0_sema", "Video Enhance 0 sema utilisation %"
)
igpu_engines_video_enhance_0_wait = Gauge(
    "igpu_engines_video_enhance_0_wait", "Video Enhance 0 wait utilisation %"
)

igpu_frequency_actual = Gauge("igpu_frequency_actual", "Frequency actual MHz")
igpu_frequency_requested = Gauge("igpu_frequency_requested", "Frequency requested MHz")

igpu_imc_bandwidth_reads = Gauge("igpu_imc_bandwidth_reads", "IMC reads MiB/s")
igpu_imc_bandwidth_writes = Gauge("igpu_imc_bandwidth_writes", "IMC writes MiB/s")

igpu_interrupts = Gauge("igpu_interrupts", "Interrupts/s")

igpu_period = Gauge("igpu_period", "Period ms")

igpu_power_gpu = Gauge("igpu_power_gpu", "GPU power W")
igpu_power_package = Gauge("igpu_power_package", "Package power W")

igpu_rc6 = Gauge("igpu_rc6", "RC6 %")


def update(data):
    igpu_engines_blitter_0_busy.set(
        data.get("engines", {}).get("Blitter/0", {}).get("busy", 0.0)
    )
    igpu_engines_blitter_0_sema.set(
        data.get("engines", {}).get("Blitter/0", {}).get("sema", 0.0)
    )
    igpu_engines_blitter_0_wait.set(
        data.get("engines", {}).get("Blitter/0", {}).get("wait", 0.0)
    )

    igpu_engines_render_3d_0_busy.set(
        data.get("engines", {}).get("Render/3D/0", {}).get("busy", 0.0)
    )
    igpu_engines_render_3d_0_sema.set(
        data.get("engines", {}).get("Render/3D/0", {}).get("sema", 0.0)
    )
    igpu_engines_render_3d_0_wait.set(
        data.get("engines", {}).get("Render/3D/0", {}).get("wait", 0.0)
    )

    igpu_engines_video_0_busy.set(
        data.get("engines", {}).get("Video/0", {}).get("busy", 0.0)
    )
    igpu_engines_video_0_sema.set(
        data.get("engines", {}).get("Video/0", {}).get("sema", 0.0)
    )
    igpu_engines_video_0_wait.set(
        data.get("engines", {}).get("Video/0", {}).get("wait", 0.0)
    )

    igpu_engines_video_enhance_0_busy.set(
        data.get("engines", {}).get("VideoEnhance/0", {}).get("busy", 0.0)
    )
    igpu_engines_video_enhance_0_sema.set(
        data.get("engines", {}).get("VideoEnhance/0", {}).get("sema", 0.0)
    )
    igpu_engines_video_enhance_0_wait.set(
        data.get("engines", {}).get("VideoEnhance/0", {}).get("wait", 0.0)
    )

    igpu_frequency_actual.set(data.get("frequency", {}).get("actual", 0))
    igpu_frequency_requested.set(data.get("frequency", {}).get("requested", 0))

    igpu_imc_bandwidth_reads.set(data.get("imc-bandwidth", {}).get("reads", 0))
    igpu_imc_bandwidth_writes.set(data.get("imc-bandwidth", {}).get("writes", 0))

    igpu_interrupts.set(data.get("interrupts", {}).get("count", 0))

    igpu_period.set(data.get("period", {}).get("duration", 0))

    igpu_power_gpu.set(data.get("power", {}).get("GPU", 0))
    igpu_power_package.set(data.get("power", {}).get("Package", 0))

    igpu_rc6.set(data.get("rc6", {}).get("value", 0))


if __name__ == "__main__":
    if os.getenv("DEBUG", False):
        debug = logging.DEBUG
    else:
        debug = logging.INFO
    logging.basicConfig(format="%(asctime)s - %(message)s", level=debug)

    start_http_server(8080)

    period = os.getenv("REFRESH_PERIOD_MS", 10000)
    device = os.getenv("DEVICE")

    if device is not None:
        cmd = "intel_gpu_top -J -s {} -d {}".format(int(period), device)
    else:
        cmd = "intel_gpu_top -J -s {}".format(int(period))

    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    logging.info("Started " + cmd)
    output = ""

    if os.getenv("IS_DOCKER", False):
        for line in process.stdout:
            line = line.decode("utf-8").strip()
            output += line

            try:
                data = json.loads(output.strip(","))
                logging.debug(data)
                update(data)
                output = ""
            except json.JSONDecodeError:
                continue
    else:
        while process.poll() is None:
            read = process.stdout.readline()
            output += read.decode("utf-8")
            logging.debug(output)
            if read == b"},\n":
                update(json.loads(output[:-2]))
                output = ""

    process.kill()

    if process.returncode != 0:
        logging.error("Error: " + process.stderr.read().decode("utf-8"))

    logging.info("Finished")
