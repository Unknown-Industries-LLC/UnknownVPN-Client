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
            RegisterUI REG = new RegisterUI();
            REG.Show();
            Hide();
        }
        private void Login_Click(object sender, EventArgs e)
        {
            var response = UnknownAPI.Login(uBox.Text, pBox.Text, ThumbPrint.Value());
            if (response.Item1)
            {
                if(Properties.Settings.Default.remember)
                {
                    Properties.Settings.Default.Username = uBox.Text;
                    Properties.Settings.Default.password = pBox.Text;
                }
                Alert.Show("Login was successful...", NotifyUI.enmType.Success);
                UserData.Username = uBox.Text;
                UserData.Password = pBox.Text;
                ClientUI frm = new ClientUI();
                Hide();
                frm.Show();
            }
            else
            {
                MessageBox.Show(response.Item2);
                Alert.Show("Login Failed", NotifyUI.enmType.Error);
            }
        }
        private void LoginUI_Load(object sender, EventArgs e)
        {
            
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
            if(!UnknownAPI.OnlineCheck())
            {
                UnknownAPI.OpenSoftether();
                Application.Exit();
            }
            uBox.Text = Properties.Settings.Default.Username;
            pBox.Text = Properties.Settings.Default.password;

            if (Properties.Settings.Default.remember) { uK_Toggle1.Toggled = true; } else { uK_Toggle1.Toggled = false; };
            
        }
        private void RememberME_ToggledChanged()
        {
            if (uK_Toggle1.Toggled) { Properties.Settings.Default.Username = uBox.Text; Properties.Settings.Default.password = pBox.Text; } else { Properties.Settings.Default.Username = string.Empty; Properties.Settings.Default.password = string.Empty; }
        }

    }
    #endregion
}

