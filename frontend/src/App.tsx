import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import Login from "@/pages/auth/Login"
import Register from "@/pages/auth/Register"
import DashboardLayout from "@/components/layout/DashboardLayout"
import History from "@/pages/dashboard/History"
import Settings from "@/pages/dashboard/Settings"
import UserManagement from "@/pages/dashboard/UserManagement"
import { GenericScraper } from "@/components/scrapers/GenericScraper"
import { SCRAPER_CONFIGS } from "@/config/scraperConfig"

// Map sidebar paths to config IDs
const PATH_TO_CONFIG_ID: Record<string, string> = {
    "linkedin-articles": "linkedin-articles",
    "linkedin-jobs": "linkedin-jobs",
    "opentable": "opentable",
    "restaurants": "restaurants",
    "reddit": "reddit",
    "reddit-threads": "reddit-threads",
    "twitter": "twitter",
    "instagram": "instagram",
    "instagram-articles": "instagram-articles",
    "youtube": "youtube",
    "google-maps": "google-maps",
    "speakers": "speakers",
    "gitex": "gitex",
    "eauctions": "eauctions",
    "london-scraper": "london-scraper",
    "india-scraper": "india-scraper",
    "gartner-scraper": "gartner-scraper",
    "bharat-2025": "bharat-2025",
    "bharat-2023": "bharat-2023",
    "bharat-fintech": "bharat-fintech",
    "fof-scraper": "fof-scraper",
    "isb-scraper": "isb-scraper",
    "lsb-scraper": "lsb-scraper",
    "nexgen-scraper": "nexgen-scraper",
    "leading-authorities": "leading-authorities",
    "uk-scraper": "uk-scraper",
    "us-scraper": "us-scraper",
    "europe-scraper": "europe-scraper",
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                <Route path="/dashboard" element={<DashboardLayout />}>
                    <Route index element={<Navigate to="/dashboard/history" replace />} />
                    <Route path="history" element={<History />} />
                    <Route path="settings" element={<Settings />} />
                    <Route path="users" element={<UserManagement />} />

                    {/* Generate routes for all scraper paths */}
                    {
                        Object.entries(PATH_TO_CONFIG_ID).map(([path, configId]) => (
                            <Route
                                key={path}
                                path={path}
                                element={
                                    <GenericScraper
                                        config={SCRAPER_CONFIGS[configId] || SCRAPER_CONFIGS['default']}
                                    />
                                }
                            />
                        ))
                    }

                    {/* Fallback for any other dashboard route */}
                    <Route path="*" element={<GenericScraper config={SCRAPER_CONFIGS['default']} />} />
                </Route >
            </Routes >
        </BrowserRouter >
    )
}

export default App
