"use client"

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { useRouter } from 'next/navigation';

export default function Page() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(null)
  const { push } = useRouter();

  const handleChangeUsername = (event) => {
    setUsername(event.target.value)
  }

  const handleChangePassword = (event) => {
    console.log(event.target.value)
    setPassword(event.target.value)
  }

  const onSignIn = () => {
    if(username == "user" && password == "user@password"){
      localStorage.setItem("Token",Date.now())
      setError(null)
      return push('/dashboard')
   }else{
    setError("Invalid username or password")
   }
  }

  useEffect(() => {
    if (localStorage.getItem("Token")) {
        const difference = localStorage.getItem("Token") - Date.now();
        if (difference < 3600000) {
          localStorage.clear();
          push("/dashboard");
        }
    }
}, []);

  return (
    <div className="flex justify-center items-center h-screen">
      <Card className='max-w-[600px] border-none'>
      <CardTitle className="text-2xl text-center">Welcome <br/> to Summarizer with Youtube Video <br/> and Documents
      </CardTitle>
        <CardHeader>
          <CardTitle className="text-xl text-center">Login</CardTitle>
          <CardDescription className=' text-center'>Please enter your username and password to login.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input id="username" type="text" placeholder="Your username" required onChange={handleChangeUsername} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" placeholder="Your password" required onChange={handleChangePassword} />
          </div>
          <p className="text-sm text-red-500">{error}</p>
        </CardContent>
        <CardFooter>
          <Button className="w-full hover:bg-white hover:text-black transition-colors" onClick={onSignIn} >Sign in</Button>
        </CardFooter>
        <p className=" mt-8 text-center text-sm pb-10">
        Created by{" "}
        <a className=" text-orange-300" href="https://ai-gurukul.vercel.app">
          AIGurukul
        </a>
      </p>
      </Card>
    </div>
  )
}