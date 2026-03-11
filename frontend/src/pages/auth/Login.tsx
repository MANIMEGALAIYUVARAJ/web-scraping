import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"

import { useState } from "react"
import { api } from "@/lib/api"

export default function Login() {
    const navigate = useNavigate()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            await api.login(email, password)
            navigate("/dashboard")
        } catch (err: any) {
            setError(err.message || "Login failed")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl animate-pulse-glow" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse-glow delay-1000" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="z-10 w-full max-w-md p-4"
            >
                <Card className="border-slate-200 bg-white shadow-2xl">
                    <CardHeader className="space-y-1">
                        <CardTitle className="text-3xl font-bold text-center bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                            Welcome Back
                        </CardTitle>
                        <CardDescription className="text-center text-slate-600">
                            Enter your credentials to access ScrapeForge Pro
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleLogin}>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Email</label>
                                <Input
                                    type="email"
                                    placeholder="name@example.com"
                                    required
                                    className="bg-white border-slate-300 focus:border-violet-500"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Password</label>
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    required
                                    className="bg-white border-slate-300 focus:border-violet-500"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            {error && <p className="text-red-500 text-sm">{error}</p>}
                        </CardContent>
                        <CardFooter className="flex flex-col space-y-4">
                            <Button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 transition-all duration-300 shadow-lg shadow-violet-900/20">
                                {loading ? "Signing in..." : "Sign In"}
                            </Button>
                            <div className="text-center text-sm text-slate-600">
                                Don't have an account?{" "}
                                <Link to="/register" className="text-violet-400 hover:text-violet-300 font-medium transition-colors">
                                    Create account
                                </Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </motion.div>
        </div>
    )
}
