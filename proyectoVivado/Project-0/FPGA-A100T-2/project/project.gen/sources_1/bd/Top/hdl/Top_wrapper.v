//Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2021.1 (lin64) Build 3247384 Thu Jun 10 19:36:07 MDT 2021
//Date        : Mon May 30 13:10:39 2022
//Host        : elPerroLinux running 64-bit Ubuntu 20.04.4 LTS
//Command     : generate_target Top_wrapper.bd
//Design      : Top_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module Top_wrapper
   (LED_A1,
    LED_A2,
    LED_A3,
    LED_A4,
    emc_clk,
    pci_reset,
    pcie_clkin_clk_n,
    pcie_clkin_clk_p,
    pcie_clkreq_l,
    pcie_mgt_rxn,
    pcie_mgt_rxp,
    pcie_mgt_txn,
    pcie_mgt_txp);
  output [0:0]LED_A1;
  output [0:0]LED_A2;
  output [0:0]LED_A3;
  output [0:0]LED_A4;
  input emc_clk;
  input pci_reset;
  input [0:0]pcie_clkin_clk_n;
  input [0:0]pcie_clkin_clk_p;
  output [0:0]pcie_clkreq_l;
  input [3:0]pcie_mgt_rxn;
  input [3:0]pcie_mgt_rxp;
  output [3:0]pcie_mgt_txn;
  output [3:0]pcie_mgt_txp;

  wire [0:0]LED_A1;
  wire [0:0]LED_A2;
  wire [0:0]LED_A3;
  wire [0:0]LED_A4;
  wire emc_clk;
  wire pci_reset;
  wire [0:0]pcie_clkin_clk_n;
  wire [0:0]pcie_clkin_clk_p;
  wire [0:0]pcie_clkreq_l;
  wire [3:0]pcie_mgt_rxn;
  wire [3:0]pcie_mgt_rxp;
  wire [3:0]pcie_mgt_txn;
  wire [3:0]pcie_mgt_txp;

  Top Top_i
       (.LED_A1(LED_A1),
        .LED_A2(LED_A2),
        .LED_A3(LED_A3),
        .LED_A4(LED_A4),
        .emc_clk(emc_clk),
        .pci_reset(pci_reset),
        .pcie_clkin_clk_n(pcie_clkin_clk_n),
        .pcie_clkin_clk_p(pcie_clkin_clk_p),
        .pcie_clkreq_l(pcie_clkreq_l),
        .pcie_mgt_rxn(pcie_mgt_rxn),
        .pcie_mgt_rxp(pcie_mgt_rxp),
        .pcie_mgt_txn(pcie_mgt_txn),
        .pcie_mgt_txp(pcie_mgt_txp));
endmodule
