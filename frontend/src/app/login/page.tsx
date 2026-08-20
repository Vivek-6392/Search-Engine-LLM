"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2, Sparkles, Lock, Mail, ArrowRight, CheckCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (localStorage.getItem("token")) {
      router.replace("/");
    }
  }, [router]);

  const loginUser = async (em: string, pw: string) => {
    const form = new URLSearchParams({ username: em, password: pw });
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Invalid email or password");
    localStorage.setItem("token", data.access_token);
    router.replace("/");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      if (mode === "register") {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Registration failed");
        setSuccess("Account created! Signing you in...");
        await loginUser(email, password);
      } else {
        await loginUser(email, password);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0d14] flex items-center justify-center relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div style={{
          position:"absolute", borderRadius:"50%", filter:"blur(80px)", opacity:0.15,
          width:400, height:400, background:"radial-gradient(circle, #6366f1, transparent)",
          top:"-10%", left:"-10%", animation:"float 8s ease-in-out infinite"
        }} />
        <div style={{
          position:"absolute", borderRadius:"50%", filter:"blur(80px)", opacity:0.12,
          width:350, height:350, background:"radial-gradient(circle, #8b5cf6, transparent)",
          bottom:"-10%", right:"-10%", animation:"float 8s ease-in-out infinite", animationDelay:"-4s"
        }} />
        <div style={{
          position:"absolute", borderRadius:"50%", filter:"blur(80px)", opacity:0.08,
          width:200, height:200, background:"radial-gradient(circle, #06b6d4, transparent)",
          top:"40%", left:"60%", animation:"float 8s ease-in-out infinite", animationDelay:"-2s"
        }} />
        <div style={{
          position:"absolute", inset:0,
          backgroundImage:"linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px)",
          backgroundSize:"50px 50px"
        }} />
      </div>

      <div className="relative z-10 w-full max-w-md mx-4">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
            style={{background:"linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow:"0 20px 40px rgba(99,102,241,0.4)"}}>
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">DeepSearch AI</h1>
          <p className="text-gray-400 text-sm mt-1">Multi-Agent Research Engine</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl p-8" style={{
          background:"rgba(22,27,34,0.85)",
          border:"1px solid rgba(255,255,255,0.08)",
          backdropFilter:"blur(20px)",
          boxShadow:"0 25px 50px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05)"
        }}>
          {/* Tab toggle */}
          <div className="flex bg-[#0f1115] rounded-xl p-1 mb-8">
            {(["login","register"] as const).map((m) => (
              <button key={m} onClick={() => { setMode(m); setError(""); setSuccess(""); }}
                className="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                style={mode === m ? {
                  background:"linear-gradient(135deg, #6366f1, #8b5cf6)",
                  color:"#fff",
                  boxShadow:"0 4px 15px rgba(99,102,241,0.35)"
                } : { color:"#9ca3af" }}>
                {m === "login" ? "Sign In" : "Create Account"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com" required
                  className="w-full bg-[#0f1115] border border-gray-700 text-gray-100 rounded-xl pl-10 pr-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all" />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input type={showPassword ? "text" : "password"} value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={mode === "register" ? "Choose a strong password" : "Your password"}
                  required
                  className="w-full bg-[#0f1115] border border-gray-700 text-gray-100 rounded-xl pl-10 pr-12 py-3 text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all" />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 rounded-xl px-4 py-3"
                style={{background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)"}}>
                <div className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
            {/* Success */}
            {success && (
              <div className="flex items-center gap-2 rounded-xl px-4 py-3"
                style={{background:"rgba(34,197,94,0.1)", border:"1px solid rgba(34,197,94,0.3)"}}>
                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                <p className="text-sm text-green-400">{success}</p>
              </div>
            )}

            {/* Submit */}
            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 text-white font-semibold py-3 rounded-xl transition-all duration-200 mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
              style={{background:"linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow:"0 4px 20px rgba(99,102,241,0.35)"}}>
              {loading
                ? <Loader2 className="w-5 h-5 animate-spin" />
                : <>{mode === "login" ? "Sign In" : "Create Account"}<ArrowRight className="w-4 h-4" /></>
              }
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
            <button onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
              {mode === "login" ? "Sign up free" : "Sign in"}
            </button>
          </p>
        </div>

        {/* Feature pills */}
        <div className="flex items-center justify-center gap-5 mt-6 text-xs text-gray-600">
          {["Multi-Agent Research","RAG + Web Search","Groq Powered"].map((f) => (
            <div key={f} className="flex items-center gap-1.5">
              <div className="w-1 h-1 rounded-full bg-indigo-500" />
              {f}
            </div>
          ))}
        </div>
      </div>

      <style jsx global>{`
        @keyframes float {
          0%,100%{transform:translate(0,0) scale(1);}
          33%{transform:translate(30px,-30px) scale(1.05);}
          66%{transform:translate(-20px,20px) scale(0.95);}
        }
      `}</style>
    </div>
  );
}
