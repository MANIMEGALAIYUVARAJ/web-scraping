
export interface User {
    userId: string;
    name: string;
    email: string;
    role: "admin" | "user";
    allowed_modules: string[];
    profile_photo?: string;
}

const STORAGE_KEY = "scrapeforge_user";

export const auth = {
    getUser: (): User | null => {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    },

    setUser: (user: User) => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
        // Dispatch custom event for reactive updates
        window.dispatchEvent(new Event("auth-change"));
    },

    clearUser: () => {
        localStorage.removeItem(STORAGE_KEY);
    },

    isAuthenticated: () => {
        return !!localStorage.getItem(STORAGE_KEY);
    },

    isAdmin: () => {
        const user = auth.getUser();
        return user?.role === "admin";
    },

    canAccessModule: (moduleId: string) => {
        const user = auth.getUser();
        if (!user) return false;
        if (user.role === "admin") return true;

        // Special case for "history" and "settings" which are always allowed
        if (moduleId === "history" || moduleId === "settings") return true;

        // "default" config is usually invalid, but let's check allowed_modules
        return user.allowed_modules.includes(moduleId);
    }
};
