import wx
from typing import Callable, Type, Any, TYPE_CHECKING
import math

from amulet.api.structure import Structure
from amulet.api.data_types import BlockCoordinates
from amulet_map_editor.amulet_wx.ui.simple import SimplePanel
from amulet_map_editor.amulet_wx.util.validators import IntValidator
from amulet_map_editor.programs.edit.canvas.ui.base_ui import BaseUI

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.canvas.edit_canvas import EditCanvas


class SelectLocationUI(SimplePanel, BaseUI):
    """A UI element that can be dropped into the EditCanvas and let the user pick a location for a structure.
    This UI does not allow for rotation.
    Will send EVT_SELECT_CONFIRM when the user confirms the selection."""

    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        structure: Structure,
        confirm_callback: Callable[[], None],
    ):
        SimplePanel.__init__(self, parent)
        BaseUI.__init__(self, canvas)

        self._structure = structure
        self.canvas.structure.clear()
        self.canvas.structure.append(structure, (0, 0, 0), (1, 1, 1), (0, 0, 0))
        self.canvas.draw_structure = True

        self._setup_ui()

        self._confirm = wx.Button(self, label="Confirm")
        self.sizer.Add(
            self._confirm, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5
        )

        self._confirm.Bind(wx.EVT_BUTTON, lambda evt: confirm_callback())

    def _add_row(self, label: str, wx_object: Type[wx.Object], **kwargs) -> Any:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_object(sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        name_text = wx.StaticText(self, label=label)
        sizer.Add(name_text, flag=wx.CENTER | wx.ALL | wx.EXPAND, border=5)
        obj = wx_object(self, **kwargs)
        sizer.Add(obj, flag=wx.CENTER | wx.ALL, border=5)
        return obj

    def _setup_ui(self):
        self._x: wx.SpinCtrl = self._add_row(
            "x", wx.SpinCtrl, min=-30000000, max=30000000
        )
        self._y: wx.SpinCtrl = self._add_row(
            "y", wx.SpinCtrl, min=-30000000, max=30000000
        )
        self._z: wx.SpinCtrl = self._add_row(
            "z", wx.SpinCtrl, min=-30000000, max=30000000
        )
        for ui in (self._x, self._y, self._z):
            ui.SetValidator(IntValidator())
        self._copy_air: wx.CheckBox = self._add_row("Copy Air", wx.CheckBox)
        self._x.Bind(wx.EVT_SPINCTRL, self._on_transform_change)
        self._y.Bind(wx.EVT_SPINCTRL, self._on_transform_change)
        self._z.Bind(wx.EVT_SPINCTRL, self._on_transform_change)

    @property
    def location(self) -> BlockCoordinates:
        return self._x.GetValue(), self._y.GetValue(), self._z.GetValue()

    @property
    def copy_air(self) -> bool:
        return self._copy_air.GetValue()

    @property
    def structure(self) -> Structure:
        return self._structure

    def _on_transform_change(self, evt):
        location, scale, rotation = self.canvas.structure.active_transform
        self.canvas.structure.set_active_transform(self.location, scale, rotation)


class SelectTransformUI(SelectLocationUI):
    """A UI element that can be dropped into the EditCanvas and let the user pick the transform for a structure.
    Will send EVT_SELECT_CONFIRM when the user confirms the selection."""

    def _setup_ui(self):
        super()._setup_ui()
        # self._sx: wx.SpinCtrl = self._add_row('sx', wx.SpinCtrlDouble, min=-100, max=100, initial=1)
        # self._sy: wx.SpinCtrl = self._add_row('sy', wx.SpinCtrlDouble, min=-100, max=100, initial=1)
        # self._sz: wx.SpinCtrl = self._add_row('sz', wx.SpinCtrlDouble, min=-100, max=100, initial=1)
        # self._sx.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)
        # self._sy.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)
        # self._sz.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)

        self._rx: wx.SpinCtrl = self._add_row(
            "rx",
            wx.SpinCtrlDouble,
            min=-30000000,
            max=30000000,
            inc=90,
            style=wx.SP_ARROW_KEYS | wx.SP_WRAP,
        )
        self._ry: wx.SpinCtrl = self._add_row(
            "ry",
            wx.SpinCtrlDouble,
            min=-30000000,
            max=30000000,
            inc=90,
            style=wx.SP_ARROW_KEYS | wx.SP_WRAP,
        )
        self._rz: wx.SpinCtrl = self._add_row(
            "rz",
            wx.SpinCtrlDouble,
            min=-30000000,
            max=30000000,
            inc=90,
            style=wx.SP_ARROW_KEYS | wx.SP_WRAP,
        )
        self._rx.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)
        self._ry.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)
        self._rz.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)

    @property
    def scale(self) -> BlockCoordinates:
        return 1, 1, 1
        # return self._sx.GetValue(), self._sy.GetValue(), self._sz.GetValue()

    @property
    def rotation(self) -> BlockCoordinates:
        return self._rx.GetValue(), self._ry.GetValue(), self._rz.GetValue()

    def _on_transform_change(self, evt):
        for ctrl in (self._rx, self._ry, self._rz):
            ctrl.SetValue(
                round((ctrl.GetValue() % 360) / 90) * 90
            )  # TODO: change this if smaller increments are allowed
        self.canvas.structure.set_active_transform(
            self.location, self.scale, tuple(math.radians(r) for r in self.rotation)
        )
