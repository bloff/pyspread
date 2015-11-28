#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
grid_panels.py
==============

Panels that can be used from within a grid cell.

The panels pop up if they are a cell result. They stay in front of the cell.
This allows dynamic and interactive cell content.

Provides
--------

 * BaseGridPanel: Basic panel that provides UI functionality for useage in grid

 * VLCPanel: Video panel that uses the VLC player

 * vlcpanel_factory: Class factory for VLCPanels

"""

import wx

import src.lib.i18n as i18n

try:
    import src.lib.vlc as vlc

except ImportError:
    vlc = None

_ = i18n.language.ugettext


class BaseGridPanel(wx.Panel):
    """Basic panel that provides UI functionality for usage in grid"""

    pass


class VLCPanel(BaseGridPanel):
    """Basic panel that provides UI functionality for useage in grid"""

    def __init__(self, parent, *args, **kwargs):
        BaseGridPanel.__init__(self, parent, *args, **kwargs)

        # filepath = "/home/mn/tmp/pyspread_video/pyspread_podcast_1.mp4"

        self.SetBackgroundColour(wx.WHITE)

        # VLC player controls
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.filepath)
        self.player.set_media(self.media)
        self.player.set_xwindow(self.GetHandle())
        #self.player.play()

        # Bindings
        # --------

        # Left click starts and holds the video
        self.Bind(wx.EVT_LEFT_DOWN, self.OnTogglePlay)

        # Double_click resets the video, i.e. starts playing from the start
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnResetPlay)

        # The mouse wheel scrolls through the video or adjusts the timer
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def adjust_video_panel(self, grid, rect):
        """Positions and resizes video panel

        Parameters
        ----------
        rect: 4-tuple of Integer
        \tRect area of video panel

        """

        panel_posx = rect[0] + grid.GetRowLabelSize()
        panel_posy = rect[1] + grid.GetColLabelSize()

        panel_scrolled_pos = grid.CalcScrolledPosition(panel_posx, panel_posy)

        self.SetPosition(panel_scrolled_pos)
        self.SetClientRect(wx.Rect(*rect))

        # TODO: Handle videos that are partly visible or that become invisible

    # Event handlers
    # --------------

    def OnTogglePlay(self, event):
        """Toggles the video status between play and hold"""

        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()
        else:
            self.player.play()

        event.Skip()

    def OnResetPlay(self, event):
        """Resets video and starts playing it"""

        self.player.stop()
        self.player.play()

    def OnMouseWheel(self, event):
        """Mouse wheel event handler"""

        if event.	ShiftDown():
            self.OnShiftVideo(event)
        else:
            self.OnAdjustVolume(event)

    def OnShiftVideo(self, event):
        """Shifts through the video"""

        length = self.player.get_length()
        time = self.player.get_time()

        if event.GetWheelRotation() < 0:
            target_time = max(0, time-length/100.0)
        elif event.GetWheelRotation() > 0:
            target_time = min(length, time+length/100.0)

        self.player.set_time(int(target_time))

    def OnAdjustVolume(self, event):
        """Changes video volume"""

        volume = self.player.audio_get_volume()

        if event.GetWheelRotation() < 0:
            target_volume = max(0, volume-10)
        elif event.GetWheelRotation() > 0:
            target_volume = min(200, volume+10)

        self.player.audio_set_volume(target_volume)

def vlcpanel_factory(filepath):
    """Returns a VLCPanel class"""

    vlc_panel_cls = VLCPanel
    VLCPanel.filepath = filepath

    return vlc_panel_cls
