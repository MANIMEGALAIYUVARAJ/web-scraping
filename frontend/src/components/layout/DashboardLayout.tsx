import { Sidebar } from "./Sidebar"
import { Outlet } from "react-router-dom"
import { motion } from "framer-motion"

export default function DashboardLayout() {
    return (
        <div className="min-h-screen bg-background">
            <Sidebar />
            <main className="pl-64 min-h-screen w-full">
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                    className="p-8 max-w-7xl mx-auto"
                >
                    <Outlet />
                </motion.div>
            </main>
        </div>
    )
}
