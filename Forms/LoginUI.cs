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
using System.Reflection;
using UnknownVPN.API;
using System.IO;
using System.IO.Compression;
using System.Runtime.InteropServices;

namespace UnknownVPN
{
    public partial class LoginUI : Form
    {
        

        public LoginUI()
        {
            InitializeComponent();
            barz.Visible = false;
            
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
        private void lBar_MouseEnter(object sender, EventArgs e)
        {
            barz.Visible = true;
        }
        private void lBar_MouseLeave(object sender, EventArgs e)
        {
            barz.Visible = false;
        }

        private void lBar2_MouseEnter(object sender, EventArgs e)
        {
            barz2.Visible = true;
        }
        private void lBar2_MouseLeave(object sender, EventArgs e)
        {
            barz2.Visible = false;
        }
        private void Close_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }          
        #endregion

        #region Functions 
        #endregion

        #region Main
        private void Register_Click(object sender, EventArgs e)
        {
            UnknownVPN.RegisterUI REG = new UnknownVPN.RegisterUI();
            REG.Show();
            Hide();
        }
        private void Login_Click(object sender, EventArgs e)
        {
            var res = UnknownAPI.UVPN_Login(uBox.Text, pBox.Text);
            if (res.ToString().Contains("Successfully"))
            {
                UnknownVPN.ClientUI client = new UnknownVPN.ClientUI();
                client.Show();
                Hide();
            }
            else
            {
                UnknownAPI.Alert(res.ToString(), NotifyUI.enmType.Error);
            }

        }
        private void LoginUI_Load(object sender, EventArgs e)
        {
            uBox.Text = Properties.Settings.Default.Username;
            pBox.Text = Properties.Settings.Default.password;

            if (Properties.Settings.Default.remember)
            {
                RememberMe.Toggled = true;

            }
            else
            {
                RememberMe.Toggled = false;
            }


            try { if (UnknownAPI.DriverCheck() == false) { Process.Start(AppDomain.CurrentDomain.BaseDirectory + @"\drivers\softether.exe"); } } catch (Exception IO) { Console.WriteLine("Error: " + IO.Message); }
            var result = UnknownAPI.UpdateCheck();
            if (result.Item1)
            {
                using (var client = new WebClient()) 
                {
                    var downloadpath = Path.GetTempFileName();
                    var executingpath = Assembly.GetExecutingAssembly().Location;
                    client.DownloadFile(result.Item2, downloadpath);
                    File.Move(executingpath, Path.GetTempFileName());
                    ZipFile.ExtractToDirectory(downloadpath, Path.GetDirectoryName(executingpath));
                    Process.Start(executingpath);
                    Application.Exit();
                }
            }

            
        }
        private void RememberME_ToggledChanged()
        {
            if (RememberMe.Toggled)
            {
                Properties.Settings.Default.Username = uBox.Text;
                Properties.Settings.Default.password = pBox.Text;
                Properties.Settings.Default.remember = true;

            }
            else
            {
                Properties.Settings.Default.Username = string.Empty;
                Properties.Settings.Default.password = string.Empty;
                Properties.Settings.Default.remember = false;
            }
            Properties.Settings.Default.Save();
        }

        private void label6_Click(object sender, EventArgs e)
        {

            UnknownVPN.Forms.ResetPwdUI PWR = new UnknownVPN.Forms.ResetPwdUI();
            PWR.Show();
            Hide();
        }
    }
    #endregion
}

