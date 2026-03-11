import { useState, useEffect, useRef } from "react"
import { api } from "@/lib/api"
import { auth, User as AuthUser } from "@/lib/auth"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent } from "@/components/ui/Card"
import { Switch } from "@/components/ui/Switch"
import {
    User,
    Database,
    Palette,
    Download,
    Shield,
    Info,
    Monitor,
    Wrench
} from "lucide-react"

interface SettingsState {
    username: string
    email: string
    theme: string
    notifications: boolean
    chrome_driver_path?: string
    chrome_version?: string
}

export default function Settings() {
    const [settings, setSettings] = useState<SettingsState>({
        username: "",
        email: "",
        theme: "dark",
        notifications: true,
        chrome_driver_path: "",
        chrome_version: "latest"
    })
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    // Profile Photo State
    const [user, setUser] = useState<AuthUser | null>(null)
    const [previewPhoto, setPreviewPhoto] = useState<string | null>(null)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [uploadingPhoto, setUploadingPhoto] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        fetchSettings()
        const currentUser = auth.getUser()
        setUser(currentUser)
        if (currentUser?.profile_photo) {
            setPreviewPhoto(currentUser.profile_photo)
        }
    }, [])

    const fetchSettings = async () => {
        try {
            const res = await fetch("/api/settings")
            const data = await res.json()
            setSettings(data)
        } catch (err) {
            console.error("Failed to load settings", err)
        } finally {
            setLoading(false)
        }
    }

    const saveSettings = async () => {
        setSaving(true)
        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settings)
            })
            alert("Settings saved!")
        } catch (err) {
            console.error("Failed to save settings", err)
            alert("Failed to save settings")
        } finally {
            setSaving(false)
        }
    }

    const handleChange = (key: string, value: any) => {
        setSettings(prev => ({ ...prev, [key]: value }))
    }

    const handlePhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0]
            setSelectedFile(file)
            // Create preview URL
            const objectUrl = URL.createObjectURL(file)
            setPreviewPhoto(objectUrl)
        }
    }

    const handleSetPhoto = async () => {
        if (!selectedFile || !user) return;

        setUploadingPhoto(true)
        try {
            const res = await api.uploadProfilePhoto(user.userId, selectedFile)
            if (res.status === "success" && res.photoUrl) {
                // Update local user state
                const updatedUser = { ...user, profile_photo: res.photoUrl }
                auth.setUser(updatedUser)
                setUser(updatedUser)
                setSelectedFile(null) // Clear selection to hide Set button
                alert("Profile photo updated!")
                // window.location.reload() // No longer needed
            }
        } catch (err: any) {
            console.error("Upload failed", err)
            alert(err.message || "Failed to upload photo")
        } finally {
            setUploadingPhoto(false)
        }
    }

    if (loading) {
        return <div className="p-10 text-center text-muted-foreground">Loading settings...</div>
    }

    return (
        <div className="space-y-8 pb-10">
            <div className="flex items-center justify-between">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight text-primary">Settings</h1>
                    <p className="text-muted-foreground">Manage your account and application preferences</p>
                </div>
                <Button onClick={saveSettings} loading={saving}>Save Changes</Button>
            </div>

            {/* Profile Settings */}
            <Card className="border-border bg-card shadow-sm overflow-hidden">
                <div className="p-6 pb-0">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <User className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-primary">Profile Settings</h2>
                            <p className="text-sm text-muted-foreground">Manage your personal information</p>
                        </div>
                    </div>

                    <div className="grid gap-8 md:grid-cols-2">
                        {/* Photo Section */}
                        <div className="flex flex-col items-center justify-center p-6 bg-blue-50/10 rounded-xl border border-dashed border-blue-300">
                            <div className="relative group">
                                <div className="h-32 w-32 rounded-full overflow-hidden ring-4 ring-blue-500 bg-blue-50 flex items-center justify-center">
                                    {previewPhoto ? (
                                        <img src={previewPhoto} alt="Profile" className="h-full w-full object-cover" />
                                    ) : (
                                        <span className="text-4xl font-bold text-blue-500">{user?.name?.[0]?.toUpperCase() || "U"}</span>
                                    )}
                                </div>
                                <div
                                    className="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                    onClick={() => fileInputRef.current?.click()}
                                >
                                    <span className="text-white text-xs font-medium">Change</span>
                                </div>
                            </div>

                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept="image/*"
                                onChange={handlePhotoSelect}
                            />

                            <div className="mt-4 flex flex-col items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => fileInputRef.current?.click()}
                                    className="text-xs"
                                >
                                    Upload from Gallery
                                </Button>

                                {selectedFile && (
                                    <Button
                                        size="sm"
                                        onClick={handleSetPhoto}
                                        disabled={uploadingPhoto}
                                        className="bg-blue-600 hover:bg-blue-700 text-xs w-full animate-in fade-in zoom-in"
                                    >
                                        {uploadingPhoto ? "Setting..." : "Set"}
                                    </Button>
                                )}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-foreground">Username</label>
                                <Input
                                    value={settings.username}
                                    onChange={(e) => handleChange("username", e.target.value)}
                                    className="bg-input border-border h-11"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-foreground">Email</label>
                                <Input
                                    value={settings.email}
                                    onChange={(e) => handleChange("email", e.target.value)}
                                    className="bg-input border-border h-11"
                                />
                            </div>
                            <div className="pt-2">
                                <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary ring-1 ring-inset ring-primary/20">
                                    {user?.role === "admin" ? "Admin" : "Pro Plan"}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="h-6"></div>
            </Card>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Scraper Preferences */}
                <Card className="border-border bg-card shadow-sm">
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                <Database className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-primary">Scraper Preferences</h2>
                                <p className="text-sm text-muted-foreground">Configure defaults</p>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-foreground">Default result limit</label>
                                    <p className="text-xs text-muted-foreground">Results per scrape</p>
                                </div>
                                <select className="h-9 rounded-md border border-input bg-input px-3 py-1 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50">
                                    <option>25 results</option>
                                    <option>50 results</option>
                                    <option>100 results</option>
                                </select>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-foreground">Apply to all scrapers</label>
                                    <p className="text-xs text-muted-foreground">Use limit across all</p>
                                </div>
                                <Switch defaultChecked />
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-foreground">Remember last scraper</label>
                                    <p className="text-xs text-muted-foreground">Auto-select recent</p>
                                </div>
                                <Switch defaultChecked />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* UI Preferences */}
                <Card className="border-border bg-card shadow-sm">
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                <Palette className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-primary">UI Preferences</h2>
                                <p className="text-sm text-muted-foreground">Customize appearance</p>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-foreground">Theme mode</label>
                                    <p className="text-xs text-muted-foreground">Color scheme</p>
                                </div>
                                <select className="h-9 rounded-md border border-input bg-input px-3 py-1 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50">
                                    <option>Dark</option>
                                    <option>Light</option>
                                    <option>System</option>
                                </select>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-foreground">Table density</label>
                                    <p className="text-xs text-muted-foreground">Data spacing</p>
                                </div>
                                <select className="h-9 rounded-md border border-input bg-input px-3 py-1 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50">
                                    <option>Comfortable</option>
                                    <option>Compact</option>
                                </select>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium text-slate-200">Micro-animations</label>
                                    <p className="text-xs text-slate-500">Smooth transitions</p>
                                </div>
                                <Switch defaultChecked />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Export & Data Settings */}
            <Card className="border-border bg-card shadow-sm">
                <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Download className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-primary">Export & Data Settings</h2>
                            <p className="text-sm text-muted-foreground">Configure data exports</p>
                        </div>
                    </div>

                    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                        <div className="space-y-3">
                            <label className="text-sm font-medium text-foreground">Default CSV filename</label>
                            <Input
                                defaultValue="scrape_{date}_{time}"
                                className="bg-input border-border h-10 font-mono text-xs"
                            />
                        </div>

                        <div className="flex items-center justify-between pt-6">
                            <div className="space-y-0.5">
                                <label className="text-sm font-medium text-foreground">Include metadata</label>
                                <p className="text-xs text-muted-foreground">Add timestamps</p>
                            </div>
                            <Switch defaultChecked />
                        </div>

                        <div className="flex items-center justify-between pt-6">
                            <div className="space-y-0.5">
                                <label className="text-sm font-medium text-foreground">Auto-download</label>
                                <p className="text-xs text-muted-foreground">After scraping</p>
                            </div>
                            <Switch />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Driver Configuration */}
            <Card className="border-border bg-card shadow-sm">
                <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Wrench className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-primary">Driver Configuration</h2>
                            <p className="text-sm text-muted-foreground">Manage ChromeDriver settings</p>
                        </div>
                    </div>

                    <div className="grid gap-6 md:grid-cols-2">
                        <div className="space-y-3">
                            <label className="text-sm font-medium text-foreground">ChromeDriver Version</label>
                            <div className="flex gap-2">
                                <select
                                    value={settings.chrome_version || "latest"}
                                    onChange={async (e) => {
                                        const newVersion = e.target.value;
                                        handleChange("chrome_version", newVersion);

                                        // Trigger auto-install
                                        setLoading(true);
                                        try {
                                            const res = await fetch("/api/install_driver", {
                                                method: "POST",
                                                headers: { "Content-Type": "application/json" },
                                                body: JSON.stringify({ version: newVersion })
                                            });
                                            const data = await res.json();
                                            if (data.success && data.settings) {
                                                setSettings(data.settings);
                                                alert(`Driver installed successfully!\nPath: ${data.path}`);
                                            } else {
                                                console.error("Install failed:", data);
                                                alert(`Failed to install driver: ${data.error || "Unknown error"}`);
                                            }
                                        } catch (err: any) {
                                            console.error("Install error:", err);
                                            alert(`Error connecting to backend: ${err.message || "Network error"}`);
                                        } finally {
                                            setLoading(false);
                                        }
                                    }}
                                    className="h-10 w-full rounded-md border border-input bg-input px-3 py-1 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="latest">Latest (Auto-Detect)</option>
                                    <option value="stable">Stable (145.0.7632.26)</option>
                                    <option value="beta">Beta (145.0.7632.26)</option>
                                    <option value="dev">Dev (146.0.7655.0)</option>
                                    <option value="canary">Canary (146.0.7665.0)</option>
                                    <option value="144">Version 144.0.7559.110</option>
                                </select>
                                <Button
                                    variant="outline"
                                    onClick={async () => {
                                        // Manual re-trigger of the current version
                                        const versionToInstall = settings.chrome_version || "latest";
                                        setLoading(true);
                                        try {
                                            const res = await fetch("/api/install_driver", {
                                                method: "POST",
                                                headers: { "Content-Type": "application/json" },
                                                body: JSON.stringify({ version: versionToInstall })
                                            });
                                            const data = await res.json();
                                            if (data.success && data.settings) {
                                                setSettings(data.settings);
                                                alert(`Driver re-installed successfully!\nPath: ${data.path}`);
                                            } else {
                                                alert(`Failed to install driver: ${data.error || "Unknown error"}`);
                                            }
                                        } catch (err: any) {
                                            alert(`Error connecting to backend: ${err.message}`);
                                        } finally {
                                            setLoading(false);
                                        }
                                    }}
                                    title="Re-install current driver"
                                >
                                    Re-install
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground">Selecting a version will auto-download/configure it.</p>
                        </div>

                        <div className="space-y-3">
                            <label className="text-sm font-medium text-foreground">Configured Path</label>
                            <div className="relative">
                                <Input
                                    readOnly
                                    value={settings.chrome_driver_path || "Not configured"}
                                    className="bg-muted text-muted-foreground border-border h-10 font-mono text-xs pr-10"
                                />
                                {settings.chrome_driver_path && (
                                    <div className="absolute right-3 top-2.5 h-2.5 w-2.5 rounded-full bg-green-500 animate-pulse" title="Active" />
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">Auto-configured path (Read-only)</p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Security */}
                <Card className="border-border bg-card shadow-sm">
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-10 w-10 rounded-lg bg-destructive/10 flex items-center justify-center">
                                <Shield className="h-5 w-5 text-destructive" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-primary">Security</h2>
                                <p className="text-sm text-muted-foreground">Account protection</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <Button variant="outline" className="w-full justify-start h-12 bg-input border-border hover:bg-muted hover:text-foreground">
                                <div className="flex items-center">
                                    <Shield className="mr-3 h-4 w-4 text-muted-foreground" />
                                    Change Password
                                </div>
                            </Button>

                            <div className="flex items-center justify-between p-4 rounded-lg bg-muted/20 border border-border">
                                <div className="flex items-center gap-3">
                                    <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                                        <Monitor className="h-4 w-4 text-muted-foreground" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-foreground">Current Session</p>
                                        <p className="text-xs text-muted-foreground">Active now</p>
                                    </div>
                                </div>
                                <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                                    Current
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* System Information */}
                <Card className="border-border bg-card shadow-sm">
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                <Info className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-primary">System Information</h2>
                                <p className="text-sm text-muted-foreground">Account details</p>
                            </div>
                        </div>

                        <div className="space-y-4 pt-2">
                            <div className="flex items-center justify-between py-2 border-b border-border">
                                <span className="text-sm text-muted-foreground">Account Created</span>
                                <span className="text-sm font-medium text-foreground">February 2, 2026</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-border">
                                <span className="text-sm text-muted-foreground">Last Login</span>
                                <span className="text-sm font-medium text-foreground">Just now</span>
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <span className="text-sm text-muted-foreground">App Version</span>
                                <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
                                    v2.4.1
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
