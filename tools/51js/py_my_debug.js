
get_my_dbg_reg = function() { 
    return new Map([
        [0xEE, "EXITR"],
        [0xEF, "EXITCODE"],
        [0xFD, "ASSERT_CONDITON"],
        [0xFE, "ASSERT_P1"],
        [0xFF, "ASSERT_P0"],
        ])
}

let vm = new _51cpu()
install_default_peripherals(vm)
vm.extend_sfr(get_my_dbg_reg)