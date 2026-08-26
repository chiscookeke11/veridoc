import React from "react"



interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode
}


export default function CustomButton({ children, ...props }: ButtonProps) {
    return (
        <button {...props} >
            {children}
        </button>
    )
}