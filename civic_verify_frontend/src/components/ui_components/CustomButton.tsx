import React from "react";

interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
    variant?: "primary" | "outline";
    icon?: React.ReactNode;
}

export default function CustomButton({
    children,
    variant = "primary",
    className = "",
    icon,
    ...props
}: ButtonProps) {

    const baseStyles = `
        h-10 px-5 rounded-sm
        font-mono text-base font-medium
        cursor-pointer
        group
        flex items-center justify-center gap-2
    `;

    const variants = {
        primary:
            "bg-white text-[#092856] hover:bg-gray-100",

        outline:
            "border border-[#6b7c99] bg-transparent text-white hover:bg-white/10",
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${className}`}
            {...props}
        >
            <span
                className="
                    w-0
                    overflow-hidden
                    group-hover:w-4
                    transition-all
                    duration-200
                    ease-in-out
                "
            >
                {icon}
            </span>

            {children}
        </button>
    );
}