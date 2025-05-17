# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2018-2021 www.open3d.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ----------------------------------------------------------------------------

# examples/python/reconstruction_system/sensors/manual_scan.py

import argparse
import datetime
import timer
import os
import open3d as o3d


class RecorderWithCallback:
    def __init__(self, config, device, filename, align_depth_to_color, arg):
        # Global flags
        self.flag_exit = False
        self.flag_record = False
        self.filename = filename
        self.output = filename
        self.save_ply = arg.save_ply
        self.align_depth_to_color = align_depth_to_color
        print(device)
        self.recorder = o3d.io.AzureKinectRecorder(config, device)
        self.timer = timer.Timer()
        if not self.recorder.init_sensor():
            raise RuntimeError('Failed to connect to sensor')

    def escape_callback(self, vis):
        self.flag_exit = True
        if self.recorder.is_record_created():
            print('Recording finished.')
        else:
            print('Nothing has been recorded.')
        return False

    def space_callback(self, vis):
        if self.flag_record:
            print('Recording paused. '
                  'Press [Space] to continue. '
                  'Press [ESC] to save and exit.')
            self.flag_record = False

        else:
            print('Recording resumed, video may be discontinuous. '
                  'Press [SPACE] to pause. '
                  'Press [ESC] to save and exit.')
            self.flag_record = True

        return False

    def save_file(self, save_filename, save_rgbd, save_idx):
        # save timestamp
        f_time = str(save_idx) + '  ' + str(datetime.datetime.now().timestamp()) + ' ' + str(
            self.timer.counter()) + '\n'
        save_filename.write(f_time)
        # save color
        color_filename = '{0}/color/{1:05d}.jpg'.format(
            self.output, save_idx)
        print('Writing to {}'.format(color_filename))
        o3d.io.write_image(color_filename, save_rgbd.color)

        # save depth
        depth_filename = '{0}/depth/{1:05d}.png'.format(
            self.output, save_idx)
        print('Writing to {}'.format(depth_filename))
        o3d.io.write_image(depth_filename, save_rgbd.depth)
        if self.save_ply:  # save to ply
            intrinsic = o3d.io.read_pinhole_camera_intrinsic('intrinsic_1536p.json')
            # print(intrinsic)
            img_depth = o3d.geometry.Image(save_rgbd.depth)
            img_color = o3d.geometry.Image(save_rgbd.color)
            rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(img_color, img_depth,
                                                                            convert_rgb_to_intensity=False)
            ply = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)
            ply_filename = '{0}/ply/{1:05d}.ply'.format(self.output, save_idx)
            o3d.io.write_point_cloud(ply_filename, ply)
            # o3d.visualization.draw_geometries([ply])

    def run(self, chosen_mode, fps_rate):
        glfw_key_escape = 256
        glfw_key_space = 32
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(glfw_key_escape, self.escape_callback)
        vis.register_key_callback(glfw_key_space, self.space_callback)

        vis.create_window('recorder', 1920, 540)
        print("Recorder initialized. Press [SPACE] to start. "
              "Press [ESC] to save and exit.")

        vis_geometry_added = False
        f = open(filename + "/timestamp.txt", "w")

        idx = 0
        time_last = datetime.datetime.now().timestamp()
        while not self.flag_exit:
            rgbd = self.recorder.record_frame(self.flag_record, self.align_depth_to_color)

            if rgbd is None:
                continue

            if not vis_geometry_added:
                vis.add_geometry(rgbd)
                vis_geometry_added = True

            vis.update_geometry(rgbd)
            vis.poll_events()
            vis.update_renderer()
            if self.flag_record:
                if chosen_mode == 'manual':
                    self.save_file(f, rgbd, idx)
                    idx = idx + 1
                    self.flag_record = False

                if chosen_mode == "auto":
                    time_now = datetime.datetime.now().timestamp()
                    if time_now - time_last >= 1 / fps_rate:
                        print('recording image in', fps_rate, 'fps,press space to pause, press esc to stop recording')
                        self.save_file(f, rgbd, idx)
                        idx = idx + 1
                        time_last = time_now

        f.close()
        self.recorder.close_record()


if __name__ == '__main__':
    print(os.environ.get('PATH'))
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--config', default='default_config.json', type=str, help='input json kinect config')
    parser.add_argument('--save_ply', default=False, help='output ply')
    parser.add_argument('--output', type=str, help='output mkv filename')
    parser.add_argument('--list',
                        action='store_true',
                        help='list available azure kinect sensors')
    parser.add_argument('--device',
                        type=int,
                        default=0,
                        help='input kinect device id')
    parser.add_argument('--align_depth_to_color',
                        default=True,
                        help='enable align depth image to color')
    args = parser.parse_args()

    if args.list:
        o3d.io.AzureKinectSensor.list_devices()
        exit()

    # if args.config is not None:
    config = o3d.io.read_azure_kinect_sensor_config(args.config)
    # else:
    #     config = o3d.io.AzureKinectSensorConfig()a

    if args.output is not None:

        filename = args.output
    else:
        filename = '{date:%Y-%m-%d-%H-%M-%S}'.format(
            date=datetime.datetime.now())
    print('Prepare writing to {}'.format(filename))

    path = filename.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        os.makedirs(path + '/depth')
        os.makedirs(path + '/color')
        if args.save_ply:
            os.makedirs(path + '/ply')
        print('create file' + path)

    device = args.device
    if device < 0 or device > 255:
        print('Unsupported device id, fall back to 0')
        device = 0
    mode_chosen = False
    while not mode_chosen:
        mode = input("input the record mode, manual or auto\n")
        if mode == "manual" or mode == "auto":
            mode_chosen = True
        else:
            print("wrong mode chosen\n")

    if mode == "auto":
        fps_input = False
        while not fps_input:
            record_fps = float(input("input the record fps (0<fps<5)\n"))
            if 0 < record_fps <= 5:
                fps_input = True
            else:
                print("wrong fps input")
    else:
        record_fps = -1

    r = RecorderWithCallback(config, device, filename,
                             args.align_depth_to_color, args)
    r.run(mode, record_fps)
