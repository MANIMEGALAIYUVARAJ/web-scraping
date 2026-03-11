
import { auth, User } from "./auth";

const API_BASE = "/api";

export const api = {
    login: async (email: string, password: string): Promise<User> => {
        const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || "Login failed");
        }

        const data = await res.json();
        // Backend returns userId, name, email, role, allowed_modules, history
        // We only store user info in auth, history is fetched separately usually
        const user: User = {
            userId: data.userId,
            name: data.name,
            email: data.email,
            role: data.role,
            allowed_modules: data.allowed_modules,
            profile_photo: data.profile_photo
        };

        auth.setUser(user);
        return user;
    },

    register: async (name: string, email: string, password: string): Promise<User> => {
        // reuse login endpoint which handles creation if name is provided
        const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || "Registration failed");
        }

        const data = await res.json();

        // If status is 'exists', it means user logged in, which is fine, but maybe we want to warn?
        // But for this app, auto-login after register is fine.

        const user: User = {
            userId: data.userId,
            name: data.name,
            email: data.email,
            role: data.role,
            allowed_modules: data.allowed_modules
        };

        auth.setUser(user);
        return user;
    },

    getUsers: async (): Promise<User[]> => {
        const res = await fetch(`${API_BASE}/users`);
        if (!res.ok) throw new Error("Failed to fetch users");
        return res.json();
    },

    updatePermissions: async (userId: string, allowed_modules: string[]) => {
        const res = await fetch(`${API_BASE}/users/permissions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ userId, allowed_modules }),
        });

        if (!res.ok) throw new Error("Failed to update permissions");
        return res.json();
    },

    uploadProfilePhoto: async (userId: string, file: File) => {
        const formData = new FormData();
        formData.append("userId", userId);
        formData.append("photo", file);

        const res = await fetch(`${API_BASE}/upload_profile_photo`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) throw new Error("Failed to upload photo");
        return res.json();
    },

    adminCreateUser: async (userData: any) => {
        const res = await fetch(`${API_BASE}/admin/create_user`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userData),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to create user");
        return data;
    }
};
