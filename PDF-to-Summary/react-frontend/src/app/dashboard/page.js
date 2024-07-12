"use client";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";

import React, { useState, useEffect } from "react";

import logo from "@/images/logo.png";
import { Checkbox } from "@/components/ui/checkbox";

export default function Home() {
  const [file, setFile] = useState();
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [Summary, setSummary] = useState([]);
  const [error, setError] = useState("");
  const [quiz, setQuiz] = useState([]);
  const [quizAnswer, setQuizAnswer] = useState({});

  const [marks, setMarks] = useState(0);

  const [valuate, setValuate] = useState(false)

  console.log(quizAnswer);

  const { push } = useRouter();

  const [userPrompt, setUserPrompt] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("Token")) {
      localStorage.clear();
      push("/");
    }
    const difference = Date.now() - localStorage.getItem("Token");
    console.log(difference);
    if (difference > 3600000) {
      localStorage.clear();
      push("/");
    }
  }, []);

  const fileAccepted = (event) => {
    setFileName(event.target.files[0].name);
    setFile(event.target.files[0]);
  };

  const anotherSummary = () => {
    setSummary("");
    setFile("");
    setFileName("");
    setError("");
    setLoading(false);
  };

  const selectAnswer = (questionNo, selectAnswer) => {
    setQuizAnswer({...quizAnswer, [`Q${questionNo}`]:selectAnswer });
  };

  const generateSummary = () => {
    console.log("Generating Summary");
    if (!file) {
      setError("Please upload a file");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("upload_file", file);
    formData.append("userPrompt", userPrompt);
    fetch("https://textsummeryapisever.onrender.com/summarize", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.log(data.error);
          setSummary([
            ...Summary,
            {
              userPrompt: userPrompt,
              summary: `<div className="bg-red-100 border border-red-400 text-red-700 px-4 rounded relative"><strong className="font-bold text-red-700">Error Occurred:</strong><br/> <span className="block sm:inline">Please reduce the length of the messages or completion.</span></div>`,
            },
          ]);
          setLoading(false);
          return;
        }
        console.log(data);

        // Replace double asterisk words with <b> tags
        const boldRegex = /\*\*(.*?)\*\*/g;
        const formattedText = data.replace(boldRegex, "<b>$1</b>");

        const regex = /^\*(.*$)/gm;
        const replacedText = formattedText.replace(regex, "<li>$1</li>");

        setSummary([
          ...Summary,
          {
            userPrompt: userPrompt,
            summary: replacedText,
          },
        ]);
        setUserPrompt("");
        setLoading(false);
      })
      .catch((error) => {
        setSummary([
          ...Summary,
          {
            userPrompt: userPrompt,
            summary: `<div className="bg-red-100 border border-red-400 text-red-700 px-4 rounded relative"><strong className="font-bold text-red-700">Error Occurred:</strong><br/> <span className="block sm:inline">Not able to complete your request</span></div>`,
          },
        ]);
        setUserPrompt("");
        setLoading(false);
      });
  };

  const generateQuiz = () => {
    console.log("Generating Quiz");
    if (!file) {
      setError("Please upload a file");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("upload_file", file);
    // formData.append("userPrompt", "axYAW7PuSIM");
    fetch("https://textsummeryapisever.onrender.com/quiz", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setQuiz(data);
        setUserPrompt("");
        setLoading(false);
      })
      .catch((error) => {
        setQuiz({
          error: `<div className="bg-red-100 border border-red-400 text-red-700 px-4 rounded relative"><strong className="font-bold text-red-700">Error Occurred:</strong><br/> <span className="block sm:inline">Not able to complete your request</span></div>`,
        });
        setUserPrompt("");
        setLoading(false);
      });
  };

  const resolveQuery = () => {
    console.log("resolveQuery");
    if (!file) {
      setError("Please upload a file");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("upload_file", file);
    formData.append("userPrompt", userPrompt);
    fetch("https://textsummeryapisever.onrender.com/chat", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.log(data.error);
          setSummary([
            ...Summary,
            {
              userPrompt: userPrompt,
              summary: `<div className="bg-red-100 border border-red-400 text-red-700 px-4 rounded relative"><strong className="font-bold text-red-700">Error Occurred:</strong><br/> <span className="block sm:inline">Please reduce the length of the messages or completion.</span></div>`,
            },
          ]);
          setLoading(false);
          return;
        }

        // Replace double asterisk words with <b> tags
        const boldRegex = /\*\*(.*?)\*\*/g;
        const formattedText = data.replace(boldRegex, "<b>$1</b>");

        const regex = /^\*(.*$)/gm;
        const replacedText = formattedText.replace(regex, "<li>$1</li>");

        setSummary([
          ...Summary,
          {
            userPrompt: userPrompt,
            summary: replacedText,
          },
        ]);
        setUserPrompt("");
        setLoading(false);
      })
      .catch((error) => {
        setSummary([
          ...Summary,
          {
            userPrompt: userPrompt,
            summary: `<div className="bg-red-100 border border-red-400 text-red-700 px-4 rounded relative"><strong className="font-bold text-red-700">Error Occurred:</strong><br/> <span className="block sm:inline">Not able to complete your request</span></div>`,
          },
        ]);
        setUserPrompt("");
        setLoading(false);
      });
  };

  const handleChange = (event) => {
    setUserPrompt(event.target.value);
  };

  const logOut = () => {
    localStorage.clear();
    push("/");
  };

  const getScore = () => {
    setMarks(quiz.filter((item,index) => item.answer == quizAnswer[`Q${index+1}`]).length);
  };

  return (
    <div className="flex flex-col h-screen items-center max-w-[700px] m-auto pt-5">
      <div className="flex justify-center mt-2">
        <Image src={logo} alt="Logo" height={100} width={100} />
      </div>
      <h1 className="text-2xl mt-5 font-bold text-center">
        Summarize & Chat with PDF
      </h1>
      <div className="m-5">
        <p className="text-md mt-2 text-center">
          Upload a PDF file and get a Summary also you can chat with PDF
        </p>
      </div>
      {quiz[0] ? (
        <>
        {valuate ? <div className="mt-5 w-full p-8 ">
          <p className="text-md text-center font-semibold">You have <br/> <span className="font-bold text-[40px]">{marks}</span> <br /> marks out of {quiz.length}</p>
        </div> : ""}
        {
          quiz.map((item, index) => {
            return (
              <div key={index} className="w-full">
                <div className={`p-4 border-2 ${valuate ? item.answer == quizAnswer[`Q${index + 1}`] ? "border-green-800" : "border-red-800" : "border-zinc-800"} mt-3 rounded-lg`}>
                <p className="text-md text-left font-semibold">
                  {(index + 1) + "] " + item.question}
                </p>
                {
                  item.options.map((option, optIndex) => {
                    return (
                      <div key={optIndex} className="flex items-center mt-2">
                        <input
                          onClick={() => selectAnswer(index +1 , optIndex +1)}
                          type="radio"
                          id={`question-${index}-option-${optIndex}`}
                          name={`question-${index}`}
                          className="h-4 w-4 mr-2 mt-[2px]"
                          disabled={valuate ? true : false}
                        />
                        <label className={`${valuate ? item.answer == optIndex + 1 ? "text-md text-left text-green-500" : quizAnswer[`Q${index + 1}`] == optIndex+1 ? "text-md text-left text-red-500" : "text-md text-left " : "text-md text-left"}`}>
                          {option}{" "} 
                        </label>
                      </div>
                    );
                  })
                }
                {
                  valuate ? item.answer == quizAnswer[`Q${index + 1}`] ? 
                  <div className="mt-4 w-full bg-green-800 rounded-lg">
                    <p className="text-md text-left text-green-100 font-semibold p-1 ml-3">Your Answer is Correct</p>
                  </div> : 
                  <div className="mt-4 w-full bg-red-800 rounded-lg">
                    <p className="text-md text-left text-red-100 font-semibold p-1 ml-3">Your Answer is Incorrect</p>
                  </div>
                  : ""
                }
                </div>
              </div>
            );
          })
        }
        <div>
          <Button className="mt-5" onClick={() => {setValuate(true),getScore()}}>
            Valuate
          </Button>
        </div>
        
        </>
        
      ) : Summary[0]?.summary ? (
        <>
          {Summary?.map((item, index) => {
            return (
              <div key={index} className="w-full px-8 mt-10">
                <p className="text-md text-left font-bold">
                  {index == 0 ? "Summary Prompt" : "Question"}
                </p>
                <div className="bg-zinc-900 p-3 rounded-lg mt-2">
                  <p className="text-md text-left">
                    {item.userPrompt == "" ? (
                      <i>User Prompt is Empty</i>
                    ) : (
                      item.userPrompt
                    )}
                  </p>
                </div>
                <p
                  dangerouslySetInnerHTML={{ __html: item.summary }}
                  className="text-md mt-5 text-left whitespace-pre-line "
                ></p>
                {/* Loop over this part */}
              </div>
            );
          })}
          {loading ? (
            <>
              <div className="m-auto my-20">
                <svg
                  aria-hidden="true"
                  className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600 m-auto mt-5"
                  viewBox="0 0 100 101"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                    fill="currentColor"
                  />
                  <path
                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                    fill="currentFill"
                  />
                </svg>
              </div>
            </>
          ) : (
            <>
              <div className="mt-10 w-full">
                <div className="bg-zinc-900 rounded-lg mx-8 px-5 md:pr-0 py-1">
                  <p className="mt-5 text-left font-semibold text-sm">
                    Chat with document
                  </p>
                  <div className="m-auto mt-3 md:flex mb-6">
                    <Input
                      id="title"
                      type="text"
                      value={userPrompt}
                      onChange={handleChange}
                      className="mb-0"
                    />
                    <Button
                      className="m-auto md:mx-5 md:mt-0 mt-5 w-full md:w-auto"
                      onClick={() => resolveQuery()}
                    >
                      Post
                    </Button>
                  </div>
                </div>
                <div className="w-fit m-auto mt-10">
                  <Button
                    variant="outline"
                    className="mt-10 m-auto"
                    onClick={() => anotherSummary()}
                  >
                    Upload New File
                  </Button>
                </div>
              </div>
            </>
          )}
        </>
      ) : loading ? (
        <>
          <p className="text-lg text-center mt-10 font-semibold">
            Loading Summary Please Wait
          </p>
          <div className="m-auto">
            <svg
              aria-hidden="true"
              className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600 m-auto mt-5"
              viewBox="0 0 100 101"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                fill="currentColor"
              />
              <path
                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                fill="currentFill"
              />
            </svg>
          </div>
        </>
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
                  onChange={fileAccepted}
                  className="max-w-[650px] pt-1.5 mt-10 mx-auto"
                />
                {error ? (
                  <p className="text-sm text-left mx-3 mt-1 font-semibold text-red-600">
                    {error}
                  </p>
                ) : (
                  ""
                )}
              </>
            )}
          </div>
          {!quiz[0] ? (
            <>
              <div className="mt-5 w-full p-8">
                <Label htmlFor="title">
                  You can provide optional instructions to create summary in
                  text box below!!
                </Label>
                <Textarea
                  id="title"
                  type="text"
                  onChange={handleChange}
                  className="mt-2"
                />
              </div>
              <div className="w-fit m-auto">
                <Button className="mt-5" onClick={() => generateSummary()}>
                  Generate Summary and Chat
                </Button>
              </div>
              <div class="inline-flex items-center justify-center w-full">
                <hr class="w-64 h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
                <span class="absolute px-3 font-medium text-gray-900 -translate-x-1/2 bg-white left-1/2 dark:text-white dark:bg-zinc-900">
                  or
                </span>
              </div>

              <div className="w-fit m-auto">
                <Button className="mt-5" onClick={() => generateQuiz()}>
                  Generate Quiz
                </Button>
              </div>
            </>
          ) : (
            ""
          )}
        </div>
      )}
      <p className="m-5 text-sm text-center mt-10">
        Click on log out to clear clear the session <br />{" "}
        <span className="text-red-400 text-sm" onClick={logOut}>
          Log Out
        </span>{" "}
      </p>
      <p className=" text-center text-sm pb-10">
        Created by{" "}
        <a className=" text-orange-300" href="https://ai-guru-kul.vercel.app">
          AIGuruKul
        </a>
      </p>
    </div>
  );
}
