
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { User } from "@/lib/auth"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Switch } from "@/components/ui/Switch"
// import { Label } from "@/components/ui/Label" // Missing
// import { Badge } from "@/components/ui/Badge" // Missing
import { Shield, Users } from "lucide-react"

// List of all available modules
// Ideally this comes from config, but let's hardcode the IDs we used in Sidebar to be safe
// Or keys from SCRAPER_CONFIGS? 
// Sidebar had: linkedin-articles, linkedin-jobs, opentable, restaurants, reddit, reddit-threads, twitter, instagram, instagram-articles, youtube, google-maps, speakers, gitex, eauctions
const ALL_MODULES = [
    { id: "linkedin-articles", label: "LinkedIn Articles" },
    { id: "linkedin-jobs", label: "LinkedIn Jobs" },
    { id: "opentable", label: "OpenTable" },
    { id: "restaurants", label: "Restaurants" },
    { id: "reddit", label: "Reddit" },
    { id: "reddit-threads", label: "Reddit Threads" },
    { id: "twitter", label: "Twitter" },
    { id: "instagram", label: "Instagram" },
    { id: "instagram-articles", label: "Instagram Articles" },
    { id: "youtube", label: "YouTube" },
    { id: "google-maps", label: "Google Maps" },
    { id: "speakers", label: "Speakers" },
    { id: "gitex", label: "Gitex Exhibitors" },
    { id: "eauctions", label: "E-Auctions" },
    { id: "london-scraper", label: "London Speakers" },
    { id: "india-scraper", label: "India Speakers" },
    { id: "gartner-scraper", label: "Gartner CFO" },
    { id: "bharat-2025", label: "Bharat 2025" },
    { id: "bharat-2023", label: "Bharat 2023" },
    { id: "bharat-fintech", label: "Bharat Fintech" },
    { id: "fof-scraper", label: "Future of Finance" },
    { id: "isb-scraper", label: "Indian Speaker Bureau" },
    { id: "lsb-scraper", label: "London Speaker Bureau" },
    { id: "nexgen-scraper", label: "NexGen Banking" },
    { id: "leading-authorities", label: "Leading Authorities" },
    { id: "uk-scraper", label: "UK Speakers" },
    { id: "us-scraper", label: "US Speakers" },
    { id: "europe-scraper", label: "Europe Speakers" },
];

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        loadUsers()
    }, [])

    const loadUsers = async () => {
        try {
            const data = await api.getUsers()
            setUsers(data)
        } catch (err: any) {
            setError(err.message || "Failed to load users")
        } finally {
            setLoading(false)
        }
    }

    const handlePermissionChange = async (userId: string, moduleId: string, checked: boolean) => {
        // Optimistic update
        const userIndex = users.findIndex(u => u.userId === userId)
        if (userIndex === -1) return

        const user = users[userIndex]
        let newModules = [...(user.allowed_modules || [])]

        if (checked) {
            if (!newModules.includes(moduleId)) newModules.push(moduleId)
        } else {
            newModules = newModules.filter(id => id !== moduleId)
        }

        const newUsers = [...users]
        newUsers[userIndex] = { ...user, allowed_modules: newModules }
        setUsers(newUsers)

        try {
            await api.updatePermissions(userId, newModules)
        } catch (err) {
            // Revert on error
            setUsers(users)
            alert("Failed to save permission")
        }
    }

    const [showCreateModal, setShowCreateModal] = useState(false)
    const [newUser, setNewUser] = useState({
        name: "",
        email: "",
        password: "",
        allowed_modules: [] as string[]
    })
    const [creating, setCreating] = useState(false)

    const handleCreateUser = async () => {
        if (!newUser.name || !newUser.email || !newUser.password) {
            alert("Please fill in all fields")
            return
        }
        setCreating(true)
        try {
            await api.adminCreateUser(newUser)
            alert("User created successfully!")
            setShowCreateModal(false)
            setNewUser({ name: "", email: "", password: "", allowed_modules: [] })
            loadUsers()
        } catch (err: any) {
            alert(err.message || "Failed to create user")
        } finally {
            setCreating(false)
        }
    }

    const toggleNewUserModule = (moduleId: string) => {
        setNewUser(prev => {
            const modules = prev.allowed_modules.includes(moduleId)
                ? prev.allowed_modules.filter(id => id !== moduleId)
                : [...prev.allowed_modules, moduleId]
            return { ...prev, allowed_modules: modules }
        })
    }

    if (loading) return <div className="p-8 text-center">Loading users...</div>
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
                    <p className="text-muted-foreground">Manage user roles and module permissions</p>
                </div>
                <Button onClick={() => setShowCreateModal(true)}>
                    <Users className="mr-2 h-4 w-4" />
                    Create New User
                </Button>
            </div>

            {/* Create User Modal - Simple inline overlay for now */}
            {showCreateModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <Card className="w-full max-w-lg border-slate-700 bg-slate-900 shadow-xl">
                        <CardHeader className="border-b border-slate-800">
                            <CardTitle>Create New User</CardTitle>
                            <CardDescription>Add a new user and assign permissions</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4 pt-4 max-h-[80vh] overflow-y-auto">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Full Name</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={newUser.name}
                                    onChange={e => setNewUser({ ...newUser, name: e.target.value })}
                                    placeholder="John Doe"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Email</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    type="email"
                                    value={newUser.email}
                                    onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                                    placeholder="john@example.com"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Password</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    type="password"
                                    value={newUser.password}
                                    onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                                    placeholder="********"
                                />
                            </div>

                            <div className="space-y-2 pt-2">
                                <label className="text-sm font-medium">Allowed Modules</label>
                                <div className="grid grid-cols-2 gap-2 border border-slate-300 bg-white rounded-md p-3 max-h-48 overflow-y-auto">
                                    {ALL_MODULES.map(module => (
                                        <div key={module.id} className="flex items-center space-x-2">
                                            <input
                                                type="checkbox"
                                                id={`new-${module.id}`}
                                                checked={newUser.allowed_modules.includes(module.id)}
                                                onChange={() => toggleNewUserModule(module.id)}
                                                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                                            />
                                            <label htmlFor={`new-${module.id}`} className="text-sm text-slate-900 cursor-pointer">
                                                {module.label}
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <Button variant="ghost" onClick={() => setShowCreateModal(false)}>Cancel</Button>
                                <Button onClick={handleCreateUser} disabled={creating}>
                                    {creating ? "Creating..." : "Create User"}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            <div className="grid gap-6">
                {users.map(user => (
                    <Card key={user.userId} className="overflow-hidden border-blue-200 bg-blue-50 text-slate-900 shadow-sm">
                        <CardHeader className="bg-blue-100/50 border-b border-blue-200 pb-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    {user.profile_photo ? (
                                        <img
                                            src={user.profile_photo}
                                            alt={user.name}
                                            className="h-10 w-10 rounded-full object-cover ring-1 ring-blue-500/20"
                                        />
                                    ) : (
                                        <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500 font-bold ring-1 ring-blue-500/20">
                                            {user.name?.[0].toUpperCase() || "U"}
                                        </div>
                                    )}
                                    <div>
                                        <CardTitle className="text-lg">{user.name}</CardTitle>
                                        <CardDescription>{user.email}</CardDescription>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {user.role === "admin" && (
                                        <span className="inline-flex items-center rounded-full border border-amber-500/50 bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-500 gap-1">
                                            <Shield className="h-3 w-3" /> Admin
                                        </span>
                                    )}
                                    <span className="inline-flex items-center rounded-full border border-blue-200 bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-700">
                                        {user.role === "admin" ? "Full Access" : "USER"}
                                    </span>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="pt-6">
                            <h3 className="text-sm font-semibold text-blue-600 mb-4 flex items-center gap-2">
                                <Database className="h-4 w-4" /> ALLOWED SCRAPER MODULES
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {ALL_MODULES.map(module => {
                                    const isChecked = user.allowed_modules?.includes(module.id)
                                    const isAdmin = user.role === "admin"

                                    return (
                                        <div key={module.id} className="flex items-center space-x-2 p-2 rounded hover:bg-blue-100 transition-colors">
                                            <Switch
                                                id={`${user.userId}-${module.id}`}
                                                checked={isAdmin || isChecked}
                                                disabled={isAdmin}
                                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handlePermissionChange(user.userId, module.id, e.target.checked)}
                                                className="data-[state=checked]:bg-blue-600 border-slate-600"
                                            />
                                            <span
                                                className={`text-sm font-medium leading-none cursor-pointer ${isAdmin ? "opacity-50" : ""}`}
                                                onClick={() => {
                                                    if (!isAdmin) {
                                                        const checkbox = document.getElementById(`${user.userId}-${module.id}`) as HTMLInputElement;
                                                        if (checkbox) {
                                                            checkbox.click();
                                                        }
                                                    }
                                                }}
                                            >
                                                {module.label}
                                            </span>
                                        </div>
                                    )
                                })}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}

import { Database } from "lucide-react"
