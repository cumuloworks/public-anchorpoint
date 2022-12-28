import platform
import anchorpoint as ap
import apsync as aps
import ffmpeg_helper
import subprocess
import re
import os
# import matplotlib.pyplot as plt

ctx = ap.Context.instance()
ui = ap.UI()

input1 = ctx.path
input1_filename = ctx.filename + "." + ctx.suffix

def compare(dialog: ap.Dialog):
    input2 = dialog.get_value("input2")
    global input2_filename
    input2_filename = os.path.basename(input2)
    ffmpeg_path = ffmpeg_helper.get_ffmpeg_fullpath()
    result_path = ctx.folder + "/psnr.txt"
    arguments = [
            ffmpeg_path,                
            "-i", input1,
            "-i", input2,
            "-lavfi", "scale2ref,psnr=stats_file=-",
            "-an",
            "-f", "null",
            "-"
        ]
    dialog.close()
    ctx.run_async(run_ffmpeg, arguments, result_path)

def run_ffmpeg(arguments, outputFilePath):
    ui.show_busy(input1)
    platform_args = {}
    if platform.system() == "Windows":
        from subprocess import CREATE_NO_WINDOW
        platform_args = {"creationflags":CREATE_NO_WINDOW}
        
    try:
        with open(outputFilePath, "w") as f:
            subprocess.run(arguments, **platform_args, stdout=f, stderr=f)
            print(load_result())
        ui.show_success("Successfully processed. (ffmpeg)")
    except Exception as e:
        ui.show_error("Something went wrong. (ffmpeg)")
    finally:
        ui.finish_busy(input1)

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

def load_result():
    with open(ctx.folder + "/psnr.txt") as result_file:
        lines = result_file.readlines()
        n_values = []
        mse_avg_values = []
        pattern = re.compile(r'n:(\d*) mse_avg:(\d*\.\d*)')

    for line in lines:
        match = pattern.match(line)
        if match:
            n_values.append(int(match.group(1)))
            mse_avg_values.append(float(match.group(2)))
    
    max_index = [i for i, x in enumerate(mse_avg_values) if x == max(mse_avg_values)][0]
    return(input1_filename + " vs " + input2_filename + "\nMAX DIFFERENCE: " + str(max(mse_avg_values)) + " (at " + str(max_index) + ")\nFRAME COMPARED: " + str(max(n_values)))
    # plt.plot(n_values, mse_avg_values)
    # plt.xlabel('n')
    # plt.ylabel('mse_avg')

    # plt.savefig(ctx.folder + '/graph.png')

ffmpeg_helper.guarantee_ffmpeg(create_dialog)