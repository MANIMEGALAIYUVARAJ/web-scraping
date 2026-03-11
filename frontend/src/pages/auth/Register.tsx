import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"

import { useState } from "react"
import { api } from "@/lib/api"

export default function Register() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        firstName: "",
        lastName: "",
        email: "",
        password: ""
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            const fullName = `${formData.firstName} ${formData.lastName}`.trim()
            if (!fullName) throw new Error("Name is required")

            await api.register(fullName, formData.email, formData.password)
            // Auto login after register
            navigate("/dashboard")

        } catch (err: any) {
            setError(err.message || "Registration failed")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 z-0">
                <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse-glow" />
                <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl animate-pulse-glow delay-1000" />
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
                            Create Account
                        </CardTitle>
                        <CardDescription className="text-center text-slate-600">
                            Join ScrapeForge Pro to start scraping
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleRegister}>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-700">First Name</label>
                                    <Input
                                        placeholder="John"
                                        required
                                        className="bg-white border-slate-300 focus:border-blue-500"
                                        value={formData.firstName}
                                        onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-700">Last Name</label>
                                    <Input
                                        placeholder="Doe"
                                        required
                                        className="bg-white border-slate-300 focus:border-blue-500"
                                        value={formData.lastName}
                                        onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Email</label>
                                <Input
                                    type="email"
                                    placeholder="name@example.com"
                                    required
                                    className="bg-white border-slate-300 focus:border-blue-500"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Password</label>
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    required
                                    className="bg-white border-slate-300 focus:border-blue-500"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                />
                            </div>
                            {error && <p className="text-red-500 text-sm">{error}</p>}
                        </CardContent>
                        <CardFooter className="flex flex-col space-y-4">
                            <Button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 transition-all duration-300 shadow-lg shadow-blue-900/20">
                                {loading ? "Creating Account..." : "Create Account"}
                            </Button>
                            <div className="text-center text-sm text-slate-600">
                                Already have an account?{" "}
                                <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                                    Sign in
                                </Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </motion.div>
        </div>
    )
}
