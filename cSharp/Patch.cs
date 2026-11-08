using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using UnityEngine;

namespace Doorstop
{
    public static class Entrypoint
    {
        public const string Warning = "\n\n\nWarning this version has been launched through SonicRaptor's launcher.\nThis may potentially lead to crashes.\n\n\n";

        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        delegate IntPtr GetPathDelegate();

        [DllImport("mono-2.0-bdwgc", CallingConvention = CallingConvention.Cdecl)]
        static extern void mono_add_internal_call([MarshalAs(UnmanagedType.LPStr)] string name, IntPtr method);

        [DllImport("mono-2.0-bdwgc", CallingConvention = CallingConvention.Cdecl)]
        static extern IntPtr mono_string_from_utf16([MarshalAs(UnmanagedType.LPWStr)] string text);

        [DllImport("mono-2.0-bdwgc", CallingConvention = CallingConvention.Cdecl)]
        static extern uint mono_gchandle_new(IntPtr obj, bool pinned);

        static GetPathDelegate getPath; //Static so the delegate is never garbage collected
        static IntPtr monoString; //MonoString kept alive by a pinned gc handle
        static string root;

        public static void Start()
        {
            root = Environment.GetEnvironmentVariable("UNITY_DATA_OVERRIDE");
            if (string.IsNullOrEmpty(root)) return; //Normal launch through the exe

            LogLater(Warning, false);

            AppDomain.CurrentDomain.AssemblyLoad += (sender, args) =>
            {
                if (args.LoadedAssembly.GetName().Name != "Assembly-CSharp") return;
                try
                {
                    Directory.CreateDirectory(root);
                    Redirect(root.Replace('\\', '/'));
                }
                catch (Exception e)
                {
                    LogLater("Failed to override persistentDataPath, using the default path.\n" + e, true);
                }
            };
        }

        static void Redirect(string path)
        {
            monoString = mono_string_from_utf16(path);
            mono_gchandle_new(monoString, true); //Keep it alive and unmoved
            getPath = () => monoString;
            var fn = Marshal.GetFunctionPointerForDelegate(getPath);

            //Register the names unity uses
            mono_add_internal_call("UnityEngine.Application::get_persistentDataPath", fn);
            mono_add_internal_call("UnityEngine.Application::get_persistentDataPath()", fn);
        }

        static void LogLater(string message, bool isError)
        {
            var thread = new Thread(() =>
            {
                Thread.Sleep(100);
                if (isError)
                {
                    Debug.LogError(message);
                }
                else {
                    Debug.LogWarning(message);
                }
            });
            thread.IsBackground = true;
            thread.Start();
        }
    }
}