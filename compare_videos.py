import platform
import anchorpoint as ap
import apsync as aps
import os
import ffmpeg_helper
import subprocess


ctx = ap.Context.instance()
ui = ap.UI()

input1 = ctx.path

def run_ffmpeg(arguments, outputFilePath):
    ui.show_busy(input1)
    platform_args = {}
    if platform.system() == "Windows":
        from subprocess import CREATE_NO_WINDOW
        platform_args = {"creationflags":CREATE_NO_WINDOW}
        
    try:
        with open(outputFilePath, "w") as f:
            subprocess.run(arguments, **platform_args, stdout=f, stderr=f)
        ui.show_success("Successfully processed. (ffmpeg)")
    except Exception as e:
        ui.show_error("Something went wrong. (ffmpeg)")
    finally:
        ui.finish_busy(input1)

def compare(dialog: ap.Dialog):
    input2 = dialog.get_value("input2")
    ffmpeg_path = ffmpeg_helper.get_ffmpeg_fullpath()
    result_path = ctx.folder + "/psnr.txt"
    arguments = [
            ffmpeg_path,                
            "-i", input1,
            "-i", input2,
            "-lavfi", "scale2ref,psnr=stats_file=-" ,
            "-an",
            "-f", "null",
            "-"
        ]
    dialog.close()
    ctx.run_async(run_ffmpeg, arguments, result_path)

def create_dialog():
    settings = aps.Settings("comparevideo")
    settings.remove("filename")

    dialog = ap.Dialog()
    dialog.title = "Compare Videos..."
    dialog.icon = ctx.icon
    dialog.add_text("Compare to", var="input2text").add_input(browse=ap.BrowseType.File, var="input2", browse_path=ctx.folder)
    dialog.add_info("Select a video file to be compared.", var="info")
    dialog.add_button("Compare", callback=compare)

    dialog.show(settings)

ffmpeg_helper.guarantee_ffmpeg(create_dialog)