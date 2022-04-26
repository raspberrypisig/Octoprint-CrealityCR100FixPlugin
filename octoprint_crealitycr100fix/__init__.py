# coding=utf-8
# This code largely based on https://github.com/SimplyPrint/OctoPrint-Creality2xTemperatureReportingFix/blob/master/octoprint_ender3v2tempfix/__init__.py

from __future__ import absolute_import, unicode_literals
import octoprint.plugin
import re


class CrealityCR100FixPlugin(octoprint.plugin.OctoPrintPlugin):
    #
    # https://community.octoprint.org/t/creality-cr-100/17385
    #
    # --- What Creality CR-100 produces as temperature report  ---
    # Send: N9 M105*46
    # Recv: Echo:Get Head(0) T:21.2/0.0
    #
    # --- What we want to produce for octoprint to be happy ---
    #
    # Send: N9 M105*46
    # Recv: ok T:21.2/0.0

    temp_report_pattern = re.compile(
        'Echo:Get Head\(0\) T:(\d+\.\d)/(\d+\.\d)')
    #fix_template = "ok T:{actual}/{target}"

    def check_for_temp_report(self, comm_instance, line, *args, **kwargs):
        # Check to see if we received the broken temperature response and if so extract temperature for octoprint
        if "T:" not in line and "Count X" not in line:
            return line

        self._logger.debug("Original: {}".format(line))

        # Fixes M114 displayed on 2 lines
        if "Count X" in line:
            line = line.replace('\n', ' ')

        else:
            m = self.temp_report_pattern.search(line)
            line = f"ok T{m.group(1)}/{m.group(2)}"

        self._logger.debug("Modified: {}".format(line))
        return line

    def get_update_information(self, *args, **kwargs):
        return dict(
            crealitycr100fix=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="raspberrypisig",
                repo="Octoprint-CrealityCR100FixPlugin",

                pip="https://github.com/raspberrypisig/Octoprint-CrealityCR100FixPlugin/archive/{target_version}.zip"
            )
        )


__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = CrealityCR100FixPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.received": (__plugin_implementation__.check_for_temp_report, 1),
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
