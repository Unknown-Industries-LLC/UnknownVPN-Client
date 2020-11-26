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
using Microsoft.Win32;
using UnknownVPN.Properties;
using UnknownVPN.API;
using UnknownVPN.API.Models;
using System.IO;
using System.IO.Compression;

namespace UnknownVPN
{
    public partial class ClientUI : Form
    {
        public ClientUI()
        {
            InitializeComponent();
            textBox1.ScrollBars = ScrollBars.Both;
            textBox1.ReadOnly = true;
        }

        #region Public/Private Declared Variables
        bool drag = false;
        public string flag = string.Empty;
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
        private void closeBTN_Click(object sender, EventArgs e)
        {
            try
            {
                if (eR_Toggle1.Toggled)
                {
                    UnknownAPI.Disconnect(ipBox.Text);
                   
                }
                if(!atkbtn.Text.Contains("Connect"))
                {
                    UnknownAPI.Disconnect(atkbtn.Tag.ToString());
                }
                //settiing changed
                atkbtn.Text = "       Connect";
                sname.Text = "• Server name: ";
                status.Text = "Status: Disconnected!";
                Alert("You have been logged out!", NotifyUI.enmType.Info);
                LoginUI login = new LoginUI();
                login.Show();
                Close();
            }
            catch (Exception LOL)
            {
                Console.Write(LOL.Message);

            }
        }
        private void tab1_Click(object sender, EventArgs e)
        {
            mPanel.Location = new Point(12, 83);
            ePanel.Location = new Point(1111, 1111);
            sPanel.Location = new Point(3333, 3333);
        }
        private void tab2_Click(object sender, EventArgs e)
        {
            ePanel.Location = new Point(12, 83);
            mPanel.Location = new Point(2222, 2222);
            sPanel.Location = new Point(3333, 3333);
        }
        private void tab3_Click(object sender, EventArgs e)
        {
            sPanel.Location = new Point(12, 83);
            mPanel.Location = new Point(2222, 2222);
            ePanel.Location = new Point(1111, 1111);
        }
        #endregion   
        #region Functions - Connect, Disconnect ect
        public void Alert(string msg, NotifyUI.enmType type)
        {
            NotifyUI frm = new NotifyUI();
            frm.showAlert(msg, type);

        }
        private void vpnCommand(string sList, string vpn_CMD, string conStatus, string btnText, string alertText, Size serList, Point serListz, bool isCustom)
        {
            atkbtn.Text = btnText;
            if (vpn_CMD == "AccountDisconnect")
            {
                UnknownAPI.Disconnect((atkbtn.Tag as ServerObject).SoftetherConnectionName);
            }
            else
            {
                UnknownAPI.Connect(sList);
            }
            status.Text = "Status: " + conStatus;
            Alert(alertText + " please wait...", NotifyUI.enmType.Info);
            pictureBox11.BackgroundImageLayout = ImageLayout.Stretch;
            if (isCustom)
            {
                sname.Text = "• Server name: Custom Server";
                pictureBox11.BackgroundImage = null;
            }
            else
            {
                sname.Text = "• Server name: " + ServerList.Text;
                try
                {
                    pictureBox11.BackgroundImage = vpnFlags.Images[(atkbtn.Tag as ServerObject).RegionCode];
                }
                catch { }
            }
        }
        #endregion
        #region Main
        private void MainUIv2_Load(object sender, EventArgs e)
        {
           
            user.Text = "• Username: " + UserData.Username;
            sub.Text = "• Subscription: " + UserData.Plan;
            foreach (var server in UnknownAPI.Servers.Keys)
            {
                ServerList.Items.Add(server);
            }
            mPanel.Location = new Point(12, 83);
            ePanel.Location = new Point(1111, 1111);
            sPanel.Location = new Point(3333, 3333);
            label1.Text = "Ver: 1.7";
        } 
        private void Connect_Click(object sender, EventArgs e)
        {
            if (!eR_Toggle1.Toggled && ServerList.Text != "")
            {
                atkbtn.Tag = UnknownAPI.Servers[ServerList.Text];
                //unknown servers
                if (atkbtn.Text.Contains("Connect"))
                {
                    pictureBox12.BringToFront();
                    vpnCommand(ServerList.Text, "AccountConnect", "Connected!", "       Disconnect", "Connecting", ServerList.Size = new Size(189, 22), ServerList.Location = new Point(37, 97), false);
                    pictureBox12.SendToBack();
                }
                else
                {
                    pictureBox12.BringToFront();
                    vpnCommand(ServerList.Text, "AccountDisconnect", "Disconnected!", "       Connect", "Disconnecting", ServerList.Size = new Size(215, 22), ServerList.Location = new Point(11, 97), false);
                    pictureBox12.SendToBack();
                }
            }
            else
            {
                //custom server
                if (atkbtn.Text.Contains("Connect"))
                {
                    vpnCommand(ipBox.Text, "AccountConnect ", "Connected!", "       Disconnect", "Connecting", ServerList.Size = new Size(215, 22), ServerList.Location = new Point(11, 97), true);
                }
                else
                {
                    vpnCommand(ipBox.Text, "AccountDisconnect ", "Disconnected!", "       Connect", "Disconnecting", ServerList.Size = new Size(215, 22), ServerList.Location = new Point(11, 97), true);
                }
            }
        }
      
        private void Discord_Click(object sender, EventArgs e)
        {
            Process.Start("https://discord.gg/rsgFNaH");
        }
        private void updatServerList_Click(object sender, EventArgs e)
        {
            Alert("Updating server list..", NotifyUI.enmType.Info);

            Servers.Text = UnknownAPI.UpdateServers();
        }
        private void updat_Click(object sender, EventArgs e)
        {
            Alert("Checking for updates..", NotifyUI.enmType.Info);
            var result = UnknownAPI.UpdateCheck();
            if(result.Item1)
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
        private void Discord1_Click(object sender, EventArgs e)
        {
            Process.Start("https://discord.gg/rsgFNaH");
        }
        private void comboBox1_DrawItem(object sender, DrawItemEventArgs e)
        {
            //this draws the flags within the combobox
            e.DrawBackground();
            e.DrawFocusRectangle();
            Color textcolor = Color.FromArgb(255, 142, 102);      
            SolidBrush myBrush = new SolidBrush(textcolor);
            if (e.Index > -1)
            {
                try
                {
                    e.Graphics.DrawImage(vpnFlags.Images[UnknownAPI.Servers.Values.ElementAt(e.Index).RegionCode], new PointF(e.Bounds.X, e.Bounds.Y));
                }
                catch (Exception ex) { MessageBox.Show(ex.Message); }
                e.Graphics.DrawString("  " + ServerList.Items[e.Index].ToString(), ServerList.Font, myBrush, new RectangleF(e.Bounds.X + 15, e.Bounds.Y + 1, e.Bounds.Width, e.Bounds.Height));
            }
        }
        private void uR_Toggle2_ToggledChanged()
        {
            if (eR_Toggle2.Toggled) { UnknownAPI.SetRunOnStartUp(true);  Properties.Settings.Default.DoStartUP = true; } else { UnknownAPI.SetRunOnStartUp(false); Properties.Settings.Default.DoStartUP = false; }
            Alert("Setting has been updated...", NotifyUI.enmType.Info);
        }
        private void button1_Click(object sender, EventArgs e)
        {
            this.WindowState = FormWindowState.Minimized;
        }
        private void SiteLink_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            Process.Start("https://unknownvpn.net/");
        }
        private void uR_Toggle1_ToggledChanged()
        {
            if (eR_Toggle1.Toggled)
            {
                ipBox.Enabled = true;
            }
            else
            {
                ipBox.Enabled = false;
            }
        }
        private void Youtube_Click(object sender, EventArgs e)
        {
            Process.Start("https://www.youtube.com/channel/UCxHBkehLw4BNAkcyl1nDUHg");
        }
        private void igpic_Click(object sender, EventArgs e)
        {
            Process.Start("https://www.instagram.com/ogcommunitys/");
        }
        #endregion
    }
}


     
     
    


