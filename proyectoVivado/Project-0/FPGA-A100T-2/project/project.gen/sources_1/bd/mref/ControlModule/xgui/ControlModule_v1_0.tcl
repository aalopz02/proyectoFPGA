# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "OP_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "WINDOW" -parent ${Page_0}


}

proc update_PARAM_VALUE.OP_WIDTH { PARAM_VALUE.OP_WIDTH } {
	# Procedure called to update OP_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.OP_WIDTH { PARAM_VALUE.OP_WIDTH } {
	# Procedure called to validate OP_WIDTH
	return true
}

proc update_PARAM_VALUE.WINDOW { PARAM_VALUE.WINDOW } {
	# Procedure called to update WINDOW when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.WINDOW { PARAM_VALUE.WINDOW } {
	# Procedure called to validate WINDOW
	return true
}


proc update_MODELPARAM_VALUE.OP_WIDTH { MODELPARAM_VALUE.OP_WIDTH PARAM_VALUE.OP_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.OP_WIDTH}] ${MODELPARAM_VALUE.OP_WIDTH}
}

proc update_MODELPARAM_VALUE.WINDOW { MODELPARAM_VALUE.WINDOW PARAM_VALUE.WINDOW } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.WINDOW}] ${MODELPARAM_VALUE.WINDOW}
}

