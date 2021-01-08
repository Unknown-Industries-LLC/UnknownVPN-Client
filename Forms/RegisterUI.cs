using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Net;
using System.Diagnostics;
using UnknownVPN.API;

namespace UnknownVPN
{
    public partial class RegisterUI : Form
    {
        public RegisterUI()
        {
            InitializeComponent();
            barz.Visible = false;

        }


        #region Public/Private Declared Variables
        bool drag = false;       
        private Point sp = new Point(0, 0); //this and drag allow a you to drag the form
        #endregion
        #region Theme/UI Events - Anything the may pertain to the action of the main interface
        private void header_MouseDown(object sender, MouseEventArgs e)
        {
            drag = true;
            sp = new Point(e.X, e.Y);
        }
        private void header_MouseMove(object sender, MouseEventArgs e)
        {
            if (drag)
            {
                Point p = PointToScreen(e.Location);
                Location = new Point(p.X - this.sp.X, p.Y - this.sp.Y);
            }
        }
        private void header_MouseUp(object sender, MouseEventArgs e)
        {
            drag = false;
        }
        private void lBar_MouseEnter(object sender, EventArgs e)
        {
            barz.Visible = true;
        }
        private void lBar_MouseLeave(object sender, EventArgs e)
        {
            barz.Visible = false;
        }
        private void button2_Click(object sender, EventArgs e)
        {
            var Login = new UnknownVPN.LoginUI();
            Login.Show();
            Close();
        }
        private void lBar_Click(object sender, EventArgs e)
        {
            
            Process.Start("https://discord.link/UnknownVPN");
        }
        #endregion
        #region Functions - Connect, disconnect, ect 
      
        public void Alert(string msg, NotifyUI.enmType type)
        {
            var frm = new UnknownVPN.NotifyUI();
            frm.showAlert(msg, type);
        }
        #endregion
        #region Main - Register
        private void lgbtn_Click(object sender, EventArgs e)
        {
            UnknownAPI.UVPN_Register(uBox.Text, pBox.Text, eBox.Text, UnknownAPI.RandomString(8), tBox.Text);
        }
    }
    #endregion
}