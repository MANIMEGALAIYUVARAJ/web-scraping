import * as React from "react"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"
// import { motion, HTMLMotionProps } from "framer-motion"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "outline" | "ghost" | "glass" | "danger"
    size?: "sm" | "md" | "lg"
    loading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "default", size = "md", loading, children, ...props }, ref) => {
        const variants = {
            default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm border-transparent",
            outline: "border border-input bg-background text-foreground hover:bg-muted hover:text-foreground",
            ghost: "hover:bg-muted hover:text-foreground text-foreground",
            glass: "bg-white/10 backdrop-blur-md text-foreground hover:bg-white/20 border border-white/20",
            danger: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        }

        const sizes = {
            sm: "h-9 px-3 text-xs",
            md: "h-10 px-4 py-2",
            lg: "h-11 px-8 text-sm",
        }

        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 active:scale-95",
                    variants[variant],
                    sizes[size],
                    className
                )}
                ref={ref}
                {...props}
            >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </button>
        )
    }
)
Button.displayName = "Button"

export { Button }
