import { Link, useLocation } from "react-router-dom"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import {
    History,
    Settings,
    Linkedin,
    Twitter,
    MapPin,
    UtensilsCrossed,
    MessageSquare,
    Video,
    Users,
    Instagram,
    Database,
    Globe,
    LogOut,
    Shield
} from "lucide-react"
import { auth } from "@/lib/auth"

// Add IDs to nav items for permission checking
const NAV_ITEMS = [
    {
        group: "LinkedIn", items: [
            { id: "linkedin-articles", name: "Articles", path: "/dashboard/linkedin-articles", icon: Linkedin },
            { id: "linkedin-jobs", name: "Jobs", path: "/dashboard/linkedin-jobs", icon: Linkedin },
        ]
    },
    {
        group: "Food & Dining", items: [
            { id: "opentable", name: "OpenTable", path: "/dashboard/opentable", icon: UtensilsCrossed },
            { id: "restaurants", name: "Restaurants", path: "/dashboard/restaurants", icon: UtensilsCrossed },
        ]
    },
    {
        group: "Social", items: [
            { id: "reddit", name: "Reddit", path: "/dashboard/reddit", icon: MessageSquare },
            { id: "reddit-threads", name: "Reddit Threads", path: "/dashboard/reddit-threads", icon: MessageSquare },
            { id: "twitter", name: "Twitter", path: "/dashboard/twitter", icon: Twitter },
            { id: "instagram", name: "Instagram", path: "/dashboard/instagram", icon: Instagram },
            { id: "instagram-articles", name: "Instagram Articles", path: "/dashboard/instagram-articles", icon: Instagram },
        ]
    },
    {
        group: "General", items: [
            { id: "youtube", name: "YouTube", path: "/dashboard/youtube", icon: Video },
            { id: "google-maps", name: "Google Maps", path: "/dashboard/google-maps", icon: MapPin },
            { id: "speakers", name: "Speakers", path: "/dashboard/speakers", icon: Users },
        ]
    },
    {
        group: "Events", items: [
            { id: "gitex", name: "Gitex Exhibitors", path: "/dashboard/gitex", icon: Globe },
            { id: "eauctions", name: "E-Auctions", path: "/dashboard/eauctions", icon: Database },
        ]
    },
    {
        group: "Speaker Bureaus", items: [
            { id: "london-scraper", name: "London Speakers", path: "/dashboard/london-scraper", icon: Globe },
            { id: "india-scraper", name: "India Speakers", path: "/dashboard/india-scraper", icon: Globe },
            { id: "gartner-scraper", name: "Gartner CFO", path: "/dashboard/gartner-scraper", icon: Shield },
            { id: "bharat-2025", name: "Bharat 2025", path: "/dashboard/bharat-2025", icon: Database },
            { id: "bharat-2023", name: "Bharat 2023", path: "/dashboard/bharat-2023", icon: Database },
            { id: "bharat-fintech", name: "Bharat Fintech", path: "/dashboard/bharat-fintech", icon: Database },
            { id: "fof-scraper", name: "Future of Finance", path: "/dashboard/fof-scraper", icon: Database },
            { id: "isb-scraper", name: "Indian Speaker Bureau", path: "/dashboard/isb-scraper", icon: Users },
            { id: "lsb-scraper", name: "London Speaker Bureau", path: "/dashboard/lsb-scraper", icon: Users },
            { id: "nexgen-scraper", name: "NexGen Banking", path: "/dashboard/nexgen-scraper", icon: Database },
            { id: "leading-authorities", name: "Leading Authorities", path: "/dashboard/leading-authorities", icon: Shield },
            { id: "uk-scraper", name: "UK Speakers", path: "/dashboard/uk-scraper", icon: Globe },
            { id: "us-scraper", name: "US Speakers", path: "/dashboard/us-scraper", icon: Globe },
            { id: "europe-scraper", name: "Europe Speakers", path: "/dashboard/europe-scraper", icon: Globe },
        ]
    },
]

export function Sidebar() {
    const location = useLocation()
    const [user, setUser] = useState(auth.getUser())
    const isAdmin = auth.isAdmin()

    useEffect(() => {
        const handleAuthChange = () => {
            setUser(auth.getUser())
        }
        window.addEventListener("auth-change", handleAuthChange)
        return () => window.removeEventListener("auth-change", handleAuthChange)
    }, [])

    // Filter nav items - ensure we return a new structure, not mutating original
    const filteredNavItems = NAV_ITEMS.map(group => ({
        ...group,
        items: group.items.filter(item => auth.canAccessModule(item.id))
    })).filter(group => group.items.length > 0)

    return (
        <div className="w-64 h-screen bg-card border-r border-border flex flex-col fixed left-0 top-0 z-50 transition-colors duration-300">
            <div className="p-6">
                <h1 className="text-xl font-bold text-primary flex items-center gap-2">
                    <Database className="h-6 w-6" />
                    ScrapeForge
                </h1>
            </div>

            <nav className="flex-1 px-4 space-y-6 pb-4 overflow-y-auto custom-scrollbar">
                {isAdmin && (
                    <div className="mb-6">
                        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2">
                            Admin Panel
                        </h2>
                        <Link
                            to="/dashboard/users"
                            className={cn(
                                "flex items-center px-2 py-2 text-sm font-semibold rounded-lg transition-all duration-200 group",
                                location.pathname === "/dashboard/users"
                                    ? "bg-amber-500/10 text-amber-500 shadow-sm ring-1 ring-amber-500/20 backdrop-blur-md"
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            )}
                        >
                            <Shield className={cn(
                                "mr-3 h-5 w-5 transition-colors",
                                location.pathname === "/dashboard/users" ? "text-amber-500" : "text-muted-foreground group-hover:text-foreground"
                            )} />
                            User Management
                        </Link>
                    </div>
                )}

                {filteredNavItems.map((group) => (
                    <div key={group.group}>
                        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2">
                            {group.group}
                        </h2>
                        <div className="space-y-1">
                            {group.items.map((item) => {
                                const isActive = location.pathname === item.path
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={cn(
                                            "flex items-center px-2 py-2 text-sm font-semibold rounded-lg transition-all duration-200 group",
                                            isActive
                                                ? "bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20 backdrop-blur-md"
                                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                        )}
                                    >
                                        <item.icon className={cn(
                                            "mr-3 h-5 w-5 transition-colors",
                                            isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                                        )} />
                                        {item.name}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>
                ))}

                <div className="pt-4 border-t border-border">
                    <Link
                        to="/dashboard/history"
                        className={cn(
                            "flex items-center px-2 py-2 text-sm font-semibold rounded-lg transition-colors mb-1",
                            location.pathname === "/dashboard/history"
                                ? "bg-primary/10 text-primary shadow-sm backdrop-blur-md"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        <History className="mr-3 h-5 w-5" />
                        History
                    </Link>
                    <Link
                        to="/dashboard/settings"
                        className={cn(
                            "flex items-center px-2 py-2 text-sm font-semibold rounded-lg transition-colors",
                            location.pathname === "/dashboard/settings"
                                ? "bg-primary/10 text-primary shadow-sm backdrop-blur-md"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        <Settings className="mr-3 h-5 w-5" />
                        Settings
                    </Link>
                </div>
            </nav>

            {/* User Profile Footer */}
            <div className="p-4 border-t border-border bg-muted/20">
                <div className="flex items-center justify-between group">
                    <div className="flex items-center gap-3">
                        {user?.profile_photo ? (
                            <img src={user.profile_photo} alt={user.name} className="h-9 w-9 rounded-full object-cover ring-1 ring-primary/20" />
                        ) : (
                            <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm ring-1 ring-primary/20">
                                {user?.name?.[0]?.toUpperCase() || "G"}
                            </div>
                        )}
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">{user?.name || "Guest"}</span>
                            <span className="text-[10px] text-muted-foreground w-24 truncate">{user?.email || "No email"}</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link to="/login" onClick={() => auth.clearUser()} className="p-2 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors">
                            <LogOut className="h-4 w-4" />
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}

