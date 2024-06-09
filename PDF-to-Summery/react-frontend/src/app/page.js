"use client";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import React, { useState, useEffect } from "react";
import pdfToText from "react-pdftotext";

import logo from "@/images/logo.png";

export default function Home() {
  const [file, setFile] = useState();
  const [fileName, setFileName] = useState("");

  const [loading, setLoading] = useState(false);
  const [pdfData, setPdfData] = useState("");
  const [summery, setSummery] = useState("");
  const [error, setError] = useState('')

  const [userPrompt, setUserPrompt] = useState('')

  const fileAccepted = (event) => {
    setFileName(event.target.files[0].name);
    setFile(event.target.files[0]);
    pdfToText(event.target.files[0]).then((text) => {
      setPdfData(text);
    });
  };

  const anotherSummery = () => {
    setSummery("");
    setFile("")
    setFileName("")
    setPdfData("")
    setError("")
    setLoading(false)
  }

  const generateSummery = () => {
    if (!pdfData) {
      setError('Please upload a file')
      return;
    }
    setLoading(true);
    fetch("https://textsummeryapisever-production.up.railway.app/summarize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        data: pdfData,
        userPrompt : userPrompt,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if(data.error){
          setSummery(`
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong className="font-bold text-red-700">Error Occurred:</strong>
      <span className="block sm:inline">${data.error}</span>
    </div>`);
          setLoading(false)
          return
        }

        // Replace double asterisk words with <b> tags
        const boldRegex = /\*\*(.*?)\*\*/g;
        const formattedText = data.replace(boldRegex, "<b>$1</b>");

        const regex = /^\*(.*$)/gm;
        const replacedText = formattedText.replace(regex, "<li>$1</li>");

        setSummery(replacedText);
        setLoading(false);
      })
      .catch((error) => {
        setError('Error in generating Summery')
        setLoading(false);
      });
  };

  const handleChange = (event) => {
    setUserPrompt(event.target.value)
  }
  return (
    <div className="flex flex-col h-screen items-center max-w-[700px] m-auto mt-10">
      <div className="flex justify-center mt-2">
        <Image src={logo} alt="Logo" height={100} width={100} />
      </div>
      <h1 className="text-3xl mt-5 font-bold">PDF to Summery</h1>
      <div>
        <p className="text-md mt-2 text-left">
          Upload a PDF file and get a summary of it
        </p>
      </div>
      {summery ? (
        <div className="w-full px-8 mt-5">
          <p className="text-lg text-center font-semibold">Summery</p>
          <p
            dangerouslySetInnerHTML={{ __html: summery }}
            className="text-md mt-5 text-left whitespace-pre-line "
          ></p>
          <div className="w-fit m-auto mt-10">
          <Button className="mt-10 m-auto" onClick={() => anotherSummery()}>
            Generate Another Summery
          </Button>
          </div>
        </div>
      ) : loading ? (
        <div>
          <p className="text-lg text-center mt-10 font-semibold">
            Loading Summery Please Wait
          </p>
          <p className="text-center"> Loading .... </p>
        </div>
      ) : (
        <div className="w-full">
          <div className="w-full px-8">
            {file ? (
              <p className="text-lg text-center mt-10 font-semibold">
                {fileName ? `Uploaded file : ${fileName}` : ""}
              </p>
            ) : (
              <>
              <Input
                type="file"
                accept=".pdf"
                onChange={fileAccepted}
                className="max-w-[650px] pt-1.5 mt-10 mx-auto"
              />
              {
                error ? (
                  <p className="text-sm text-left mx-3 mt-1 font-semibold text-red-600">
                    {error}
                  </p>
                ) : ''
              }
              </>
            )}
          </div>
          <div className="mt-5 w-full p-8">
            <Label htmlFor="title">
              You can give instructions or focus point on which Summery will be
              based
            </Label>
            <Textarea id="title" type="text" onChange={handleChange} className="mt-2" />
          </div>
          <div className="w-fit m-auto">
            <Button className="mt-5" onClick={() => generateSummery()}>
              Generate Summery
            </Button>
          </div>
        </div>
      )}

      <p className="mt-10 text-center text-sm pb-10">Created by Tanmay Singewar</p>
    </div>
  );
}
