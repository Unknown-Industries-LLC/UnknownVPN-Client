using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using UnknownVPN.API;

namespace UnknownVPN.Forms
{
    public partial class ResetPwdUI : Form
    {
        public ResetPwdUI()
        {
            InitializeComponent();
        }



        #region Public/Private Declared Variables
        bool drag = false;
        private Point sp = new Point(0, 0); //this and drag allow a you to drag the form
        #endregion
        #region Theme/UI Events - Anything the may pertain to the action of the main interface
        //the following are dragging the forum
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
        #endregion

       

        private void CloseBTN_Click(object sender, EventArgs e)
        {
            var Login = new UnknownVPN.LoginUI();
            Login.Show();
            Close();
        }

        private void ResetBTN_Click(object sender, EventArgs e)
        {
            UnknownAPI.UVPN_PwReset(uBox.Text, opBox.Text, npBox.Text);
        }
    }
}
