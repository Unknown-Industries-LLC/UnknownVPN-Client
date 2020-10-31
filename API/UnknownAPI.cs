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

namespace UnknownVPN.API
{

    public class ThumbPrint
    {
        private static string fingerPrint = string.Empty;
        public static string Value()
        {
            if (string.IsNullOrEmpty(fingerPrint))
            {
                fingerPrint = GetHash("CPU >> " + CPUId() + "\nBIOS >> " + BiosId() + "\nBASE >> " + BaseId());
            }
            return fingerPrint;
        }
        private static string GetHash(string s)
        {
            MD5 sec = new MD5CryptoServiceProvider();
            ASCIIEncoding enc = new ASCIIEncoding();
            byte[] bt = enc.GetBytes(s);
            return GetHexString(sec.ComputeHash(bt));
        }
        private static string GetHexString(byte[] bt)
        {
            string s = string.Empty;
            for (int i = 0; i < bt.Length; i++)
            {
                byte b = bt[i];
                int n, n1, n2;
                n = (int)b;
                n1 = n & 15;
                n2 = (n >> 4) & 15;
                if (n2 > 9)
                    s += ((char)(n2 - 10 + (int)'A')).ToString();
                else
                    s += n2.ToString();
                if (n1 > 9)
                    s += ((char)(n1 - 10 + (int)'A')).ToString();
                else
                    s += n1.ToString();
                if ((i + 1) != bt.Length && (i + 1) % 2 == 0) s += "-";
            }
            return s;
        }
        #region Original Device ID Getting Code
        private static string Identifier(string wmiClass, string wmiProperty)
        {
            string result = "";
            System.Management.ManagementClass mc = new System.Management.ManagementClass(wmiClass);
            System.Management.ManagementObjectCollection moc = mc.GetInstances();
            foreach (System.Management.ManagementObject mo in moc)
            {
                //Only get the first one
                if (result == "")
                {
                    try
                    {
                        result = mo[wmiProperty].ToString();
                        break;
                    }
                    catch
                    {
                    }
                }
            }
            return result;
        }
        private static string CPUId()
        {
            //Uses first CPU identifier available in order of preference
            //Don't get all identifiers, as it is very time consuming
            string retVal = Identifier("Win32_Processor", "UniqueId");
            if (retVal == "") //If no UniqueID, use ProcessorID
            {
                retVal = Identifier("Win32_Processor", "ProcessorId");
                if (retVal == "") //If no ProcessorId, use Name
                {
                    retVal = Identifier("Win32_Processor", "Name");
                    if (retVal == "") //If no Name, use Manufacturer
                    {
                        retVal = Identifier("Win32_Processor", "Manufacturer");
                    }
                    //Add clock speed for extra security
                    retVal += Identifier("Win32_Processor", "MaxClockSpeed");
                }
            }
            return retVal;
        }
        //BIOS Identifier
        private static string BiosId()
        {
            return Identifier("Win32_BIOS", "Manufacturer")
            + Identifier("Win32_BIOS", "SMBIOSBIOSVersion")
            + Identifier("Win32_BIOS", "IdentificationCode")
            + Identifier("Win32_BIOS", "SerialNumber")
            + Identifier("Win32_BIOS", "ReleaseDate")
            + Identifier("Win32_BIOS", "Version");
        }
        //Motherboard ID
        private static string BaseId()
        {
            return Identifier("Win32_BaseBoard", "Model")
            + Identifier("Win32_BaseBoard", "Manufacturer")
            + Identifier("Win32_BaseBoard", "Name")
            + Identifier("Win32_BaseBoard", "SerialNumber");
        }
        #endregion
    }
    public static class UnknownAPI
    {
        public static Dictionary<string, ServerObject> Servers = new Dictionary<string, ServerObject>();
        static UnknownAPI()
        {
            Servers.Add("[Game] OVH - Que CA 1", new ServerObject { SoftetherConnectionName = "OVH1", IP = "167.114.58.193", RegionCode = "CA" });
            Servers.Add("[Game] OVH - Que CA 2", new ServerObject { SoftetherConnectionName = "OVH2", IP = "158.69.11.135", RegionCode = "CA" });
            Servers.Add("[Game] OVH - Que CA 3", new ServerObject { SoftetherConnectionName = "OVH3", IP = "167.114.29.161", RegionCode = "CA" });
            Servers.Add("[Game] OVH - Lon GB 1", new ServerObject { SoftetherConnectionName = "OVH4", IP = "51.89.176.238", RegionCode = "GB"});
            Servers.Add("[Streaming] CHPA - Los US West 1", new ServerObject { SoftetherConnectionName = "CHPA1", IP = "149.28.85.22", RegionCode = "US" });
            Servers.Add("[Streaming] CHPA - Flo US East 1", new ServerObject { SoftetherConnectionName = "CHPA2", IP = "137.220.56.195", RegionCode = "US" });
            Servers.Add("[Streaming] IPC - AFR SY East 1", new ServerObject { SoftetherConnectionName = "IPC1", IP = "45.141.58.93", RegionCode = "AF" });
        }
        #region Public/Private Declared Variables 
        public static string[] _message = { "Success", "User Not Added", "UhOH Big Boi!", 
            "Unsuccessful: Invalid Credentials!", "Something went wrong!, reloading ak-47.....", "Unable To Connect" };
        // "149.28.118.249"
        public static string ServerIP = "167.114.215.80";
        #endregion

        #region UnknownAPI Functions - Connect, disconnect, login, register ect
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
                Process cmd = new Process();
                cmd.StartInfo.FileName = "cmd.exe";
                cmd.StartInfo.RedirectStandardInput = true;
                cmd.StartInfo.RedirectStandardOutput = true;
                cmd.StartInfo.CreateNoWindow = true;
                cmd.StartInfo.UseShellExecute = false;
                cmd.Start();
                cmd.StandardInput.WriteLine("cd " + PF);
                System.Threading.Thread.Sleep(200);
                cmd.StandardInput.WriteLine(input);
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
            return Servers[servername].SoftetherConnectionName;
        }
        public static string GetServerAddr(string servername)
        {
            return Servers[servername].IP;
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
            string res = ProcessWebRequest("http://" + ServerIP + "/version.txt");
            if (string.IsNullOrWhiteSpace(res) || !res.Contains("|")) return new Tuple<bool, string>(false, null);
            string[] data = res.Split('|');
            Version version1 = Assembly.GetExecutingAssembly().GetName().Version;
            if(Version.TryParse(data[0], out Version result))
            {
                if(result > version1)
                {
                    return new Tuple<bool, string>(true, data[1]);
                }
            }
            return new Tuple<bool, string>(false, null);
        }
        public static string UpdateServers()
        {
            var result = MessageBox.Show("Would you like to set a password now.\n If not you will need to set one manually later?", "Question?",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            foreach (var server in Servers.Values)
            {
                ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountCreate {server.SoftetherConnectionName} /SERVER:{server.IP}:443 /HUB:VPN /USERNAME:{UserData.Username} /NICNAME:VPN");
                if (result == DialogResult.Yes)
                {
                    ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountPasswordSet {server.SoftetherConnectionName} /PASSWORD:{UserData.Password} /TYPE:standard");
                }
            }
            return $"• Server Count: {Servers.Keys.Count}";
        }
        public static void Connect(string vpnOVH)
        {
            ProcessCommand("vpncmd.exe /CLIENT localhost /CMD AccountConnect " + Servers[vpnOVH].SoftetherConnectionName);
        }
        public static void Disconnect(string vpnOVH)
        {
            ProcessCommand("vpncmd.exe /CLIENT localhost /CMD AccountDisconnect " + vpnOVH);
        }
        public static void SetSoftetherUserPasswords(string pWord)
        {
            foreach (var server in Servers.Values)
            {
                ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountPasswordSet+{server.SoftetherConnectionName}/PASSWORD:" + pWord + " /TYPE:standard");
            }
        }
        public static void MakeSoftetherUsers(string vpnUser)
        {
            foreach (var server in Servers.Values)
            {
                ProcessCommand($"vpncmd.exe /CLIENT localhost /CMD AccountCreate {server.SoftetherConnectionName}/SERVER:{server.IP}:443 /HUB:VPN /USERNAME:{vpnUser} /NICNAME:VPN");
            }
        }
        public static Tuple<bool, string> Login(string user, string pass, string uID)
        {
            var url = $"http://{ServerIP}/auth2.php?user={user}&pass={pass}&uid={uID}";
            var res = ProcessWebRequest(url);
            string[] data = res.Split('|');
            if (data[0].Contains(_message[0]))
            {
                UserData.Plan = data[1];
                return new Tuple<bool, string>(true, data[0]);
            }
            else if (data[0].Contains(_message[4]))
            {
                return new Tuple<bool, string>(false, data[0]);
            }
            else if ((data[0].Contains(_message[2])))
            {
                return new Tuple<bool, string>(false, data[0]);
            }
            return new Tuple<bool, string>(false, data[0]);
        }
        public static bool Registration(string user, string pass, string email, string uID, string token)
        {
            var url = $"http://{ServerIP}/adduser2.php?user={user}&pass={pass}&email={email}&uid={uID}&token={token}";
            var res = ProcessWebRequest(url);
            if (res.Contains(_message[0]))
            {
                return true;
            }
            else if (res.Contains(_message[1]))
            {
                return false;
            }
            else if ((res.Contains(_message[2])))
            {
                return false;
            }
            return false;
        }
        #endregion
    }
    public static class UserData
    {
        public static string Username { get; set; }
        public static string Password { get; set; }
        public static string Plan { get; set; }
    }
}


