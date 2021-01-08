using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Diagnostics;
using Microsoft.Win32;
using System.Windows.Forms;
using System.Reflection;
using System.IO;
using System.Security.Cryptography;
using UnknownVPN.API.Models;
using System.Net.Http;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace UnknownVPN.API
{

    public static class UnknownAPI
    {
        #region Public Varibles/ServerObject - Host, Client, responses ect
        public static string data, message = "";
        public static string Host = "https://api.unknownvpn.net/";
        private static readonly Random _random = new Random();
        public static Dictionary<string, ServerObject> ServerList = new Dictionary<string, ServerObject>();
        #endregion
        #region UnknownAPI Functions - Connect, disconnect, login, register ect
        public static void Alert(string msg, NotifyUI.enmType type)
        {
            NotifyUI frm = new NotifyUI();
            frm.showAlert(msg, type);
        }

        public static async Task<string> GetURI(Uri u)
        {
            var response = string.Empty;
            using (var client = new HttpClient())
            {
                HttpResponseMessage result = await client.GetAsync(u);
                if (result.IsSuccessStatusCode)
                {
                    response = await result.Content.ReadAsStringAsync();
                }
            }
            return response;
        }

        public static string RandomString(int size, bool lowerCase = false)
        {
            var builder = new StringBuilder(size); //some code from stackoverflow not be my: Joshua 1/6/2021

            // Unicode/ASCII Letters are divided into two blocks
            // (Letters 65–90 / 97–122):
            // The first group containing the uppercase letters and
            // the second group containing the lowercase.  

            // char is a single Unicode character  
            char offset = lowerCase ? 'a' : 'A';
            const int lettersOffset = 26; // A...Z or a..z: length=26  

            for (var i = 0; i < size; i++)
            {
                var @char = (char)_random.Next(offset, offset + lettersOffset);
                builder.Append(@char);
            }

            return lowerCase ? builder.ToString().ToLower() : builder.ToString();
        }

        public static async Task<string> PostURI(Uri u, HttpContent c)
        {
            var response = string.Empty;
            using (var client = new HttpClient())
            {
                HttpResponseMessage result = await client.PostAsync(u, c);
                if (result.IsSuccessStatusCode)
                {
                    response = await result.Content.ReadAsStringAsync();
                }
            }
            return response;
        }

        public static async void UVPN_Register(string user, string pass, string email, string xuid, string token)
        {
            try
            {
                using (HttpClient Client = new HttpClient())
                {
                    var userData = new Dictionary<string, string>
                    {
                        {"username", user },
                        {"password", pass },
                        {"email", email },
                        {"xuid", xuid },
                         {"key", token }
                    };

                    var BaseAddr = Client.BaseAddress = new Uri($"{Host}/v3/User/signup.php");
                    var content = new FormUrlEncodedContent(userData);
                    var response = await Client.PostAsync(BaseAddr, content);
                    var responseString = await response.Content.ReadAsStringAsync();
                   if (responseString.Contains("Success"))
                    {
                        Alert("Account created Successfully...", NotifyUI.enmType.Success);
                     
                        MakeSoftetherUsers(user);
                        SetSoftetherUserPasswords(pass);
                    }
                    else
                    {
                        MessageBox.Show(responseString + Environment.NewLine + "OOPS: Seems like something went wrong!\nPlease check your information\nand try again.", "OOPS!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                    BaseAddr = null;
                }
            }
            catch (System.Threading.Tasks.TaskCanceledException tsk)
            {
                Console.Write(tsk.Message);
            }
            catch (HttpRequestException rqs)
            {
                Console.Write(rqs.Message);
            }

        }

        public static async void UVPN_PwReset(string user, string pass, string newpass)
        {
            try
            {
                using (HttpClient Client = new HttpClient())
                {
                    var userData = new Dictionary<string, string>
                    {
                    {"username", user },
                    {"password", pass },
                    {"newpass", newpass }
                    };


                    var BaseAddr = Client.BaseAddress = new Uri($"{Host}/v3/User/resetpasswrd.php");
                    var content = new FormUrlEncodedContent(userData);
                    var response = await Client.PostAsync(BaseAddr, content);
                    var responseString = await response.Content.ReadAsStringAsync();

                    if (responseString.Contains("Successfully"))
                    {
                        BaseAddr = null;
                        SetSoftetherUserPasswords(pass);
                        Alert("Successfully reset password...", NotifyUI.enmType.Success);                   
                    }
                    else
                    {
                        MessageBox.Show(responseString + Environment.NewLine + "OOPS: Seems like something went wrong!\nPlease check your information\nand try again.", "OOPS!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
            catch (System.Threading.Tasks.TaskCanceledException tsk)
            {
                Console.Write(tsk.Message);
            }
            catch (HttpRequestException rqs)
            {
                Console.Write(rqs.Message);
            }
        
           
        }

        public static string UVPN_Login(string username, string password)
        {
            try
            {
                var t = Task.Run(() => GetURI(new Uri($"{Host}/v3/User/login.php?username={username}&password={password}")));
                t.Wait();
                dynamic _UserData = JObject.Parse(t.Result);

                UserData.Status = _UserData.status;
                UserData.Message = _UserData.message;
                message = _UserData.message;

                if (UserData.Status == true)
                {

                    UserData.Count = _UserData.count;
                    UserData.Username = _UserData.username;
                    UserData.Password = _UserData.password;
                    UserData.Email = _UserData.email;
                    UserData.Plan = _UserData.plan;


                    string str0 = _UserData.servers.ToString().Replace("[", "");
                    string str1 = str0.Replace("]", "");
                    string[] str2 = str1.Split(',');

                    ServerList.Clear();
                    for (int i = 0; i < Convert.ToInt32(UserData.Count); i++)
                    {
                        string ip = str2[i].Replace(@"""", "");


                        ServerList.Add("UVPN_Server" + i.ToString(), new ServerObject { SoftetherConnectionName = "UVPN_Server" + i.ToString(), IP = str2[i].Replace(@"""", ""), RegionCode = "U" });
                        if (i >= Convert.ToInt32(UserData.Count))
                        {
                            break;
                        }

                    }

                }
                else
                {

                    return message.ToString();
                }
            }
            catch (System.Threading.Tasks.TaskCanceledException tsk)
            {
                Console.Write(tsk.Message);
            }
            catch (HttpRequestException rqs)
            {
                Console.Write(rqs.Message);
            }

            return message.ToString();
        }

        private static string ProcessWebRequest(string host)
        {
            try
            {
                using (WebClient wc = new WebClient())
                {
                    return wc.DownloadString(host);
                }
            }
            catch (Exception e)
            {
                return e.Message;
            }
        }

        private static void ProcessCommand(string input)
        {
            try
            {
                string PF = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "SoftEther VPN Client");
                //System.IO.DirectoryInfo PF = new System.IO.DirectoryInfo(Environment.GetFolderPath(Environment.SpecialFolder.System).Substring(0, 1) + @":\Program Files\SoftEther VPN Client\");
                Process cmd = new Process();
                cmd.StartInfo.FileName = "cmd.exe";
                cmd.StartInfo.RedirectStandardInput = true;
                cmd.StartInfo.RedirectStandardOutput = true;
                cmd.StartInfo.CreateNoWindow = true;
                cmd.StartInfo.UseShellExecute = false;
                cmd.Start();
                System.Threading.Thread.Sleep(200);
                cmd.StandardInput.WriteLine(input);
                cmd.StandardOutput.Read();
                System.Threading.Thread.Sleep(200);
                cmd.StandardInput.Flush();
                cmd.StandardInput.Close();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }

        public static string GetConName(string servername)
        {
            return ServerList[servername].SoftetherConnectionName;
        }

        public static string GetServerAddr(string servername)
        {
            return ServerList[servername].IP;
        }

        public static bool SetRunOnStartUp(bool startup)
        {
            using (RegistryKey key = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true))
            {
                if (startup)
                {
                    key.SetValue("UnknownVPN", "\"" + Application.ExecutablePath + "\"");
                    return true;
                }
                else
                {
                    key.DeleteValue("UnknownVPN", false);
                    return false;
                }
            }
        }

        public static bool DriverCheck()
        {
            if (!Directory.Exists(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "SoftEther VPN Client")))
            {
                return false;
            }
            else if (!File.Exists(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "SoftEther VPN Client", "vpncmd.exe")))
            {
                return false;
            }
            return true;
        }

        public static Tuple<bool, string> UpdateCheck()
        {
            string res = ProcessWebRequest($"{Host}/version.txt");
            if (string.IsNullOrWhiteSpace(res) || !res.Contains("|")) return new Tuple<bool, string>(false, null);
            string[] data = res.Split('|');
            Version version1 = Assembly.GetExecutingAssembly().GetName().Version;
            if (Version.TryParse(data[0], out Version result))
            {
                if (result > version1)
                {
                    return new Tuple<bool, string>(true, data[1]);
                }
            }
            return new Tuple<bool, string>(false, null);
        }

        public static string UpdateServers()
        {

            var result = MessageBox.Show("Would you like to set a password now.\n If not you will need to set one manually later?", "Question?", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            foreach (var server in ServerList.Values)
            {

                string LOL = server.IP.Replace(Environment.NewLine + "  ", "");
                string sip = LOL.Replace(Environment.NewLine, "");
                ProcessCommand("vpncmd.exe /CLIENT localhost /CMD AccountCreate " + server.SoftetherConnectionName + " /SERVER:" + sip + ":5555 /HUB:VPN /USERNAME:" + UserData.Username + " /NICNAME:VPN");
                if (result == DialogResult.Yes)
                {
                    ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountPasswordSet " + server.SoftetherConnectionName + " /PASSWORD:" + UserData.Password + " /TYPE:standard");
                }
            }
            return $"• Server Count: {ServerList.Keys.Count}";
        }

        public static void Connect(string vpnOVH)
        {
            ProcessCommand("vpncmd.exe /CLIENT localhost /CMD AccountConnect " + ServerList[vpnOVH].SoftetherConnectionName);
        }

        public static void Disconnect(string vpnOVH)
        {
            ProcessCommand("vpncmd.exe /CLIENT localhost /CMD AccountDisconnect " + vpnOVH);
        }

        public static void SetSoftetherUserPasswords(string pWord)
        {
            foreach (var server in ServerList.Values)
            {
                ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountPasswordSet {server.SoftetherConnectionName} /PASSWORD:" + pWord + " /TYPE:standard");
            }
        }

        public static void MakeSoftetherUsers(string vpnUser)
        {
            foreach (var server in ServerList.Values)
            {
                ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountCreate {server.SoftetherConnectionName} /SERVER:{server.IP}:5555 /HUB:VPN /USERNAME:{vpnUser} /NICNAME:VPN");
            }
        }
        #endregion
    }

    public static class UserData
    {
        //server data
        public static Boolean Status { get; set; }
        //userdata
        public static string Count { get; set; }
        public static string Username { get; set; }
        public static string Password { get; set; }
        public static string Email { get; set; }
        public static string Plan { get; set; }
        public static string Message { get; set; }


    }
}


