"use client";

import type React from "react";

import { useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Upload, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface PredictionResult {
  disease: string;
  solution: {
    Cause: string;
    "Peak Season": string;
    Remedy: string;
  };
  confidence: number;
}

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
      setResult(null);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage) return;

    setIsLoading(true);
    setError(null);

    try {
      // Create a FormData object to send the actual image file
      const formData = new FormData();

      // Get the file from the input element
      const fileInput = document.getElementById(
        "image-upload"
      ) as HTMLInputElement;
      const file = fileInput.files?.[0];

      if (!file) {
        throw new Error("No file selected");
      }

      // Append the file to the FormData object
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        // Don't set Content-Type header when using FormData, it will be set automatically
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to get prediction");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 md:p-24">
      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle>Crop Disease Detector</CardTitle>
          <CardDescription>
            Upload an image to detect crop diseases and get solutions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center justify-center">
            <label
              htmlFor="image-upload"
              className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-4 text-muted-foreground" />
                <p className="mb-2 text-sm text-muted-foreground">
                  <span className="font-semibold">Click to upload</span> or drag
                  and drop
                </p>
                <p className="text-xs text-muted-foreground">
                  PNG, JPG or JPEG
                </p>
              </div>
              <input
                id="image-upload"
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleImageChange}
              />
            </label>
          </div>

          {selectedImage && (
            <div className="flex flex-col items-center">
              <div className="relative w-full max-w-md h-64 overflow-hidden rounded-lg">
                <Image
                  src={selectedImage || "/placeholder.svg"}
                  alt="Selected crop"
                  fill
                  className="object-contain"
                  unoptimized={selectedImage?.startsWith("data:")}
                />
              </div>
              <Button
                className="mt-4"
                onClick={handleSubmit}
                disabled={isLoading}
              >
                {isLoading ? "Processing..." : "Analyze Image"}
              </Button>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <div className="mt-6 space-y-4 border rounded-lg p-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Disease Detected:</h3>
                <span className="text-lg">{result.disease}</span>
              </div>

              <div>
                <h4 className="font-medium mb-2">Solution:</h4>
                <div className="space-y-2 pl-4">
                  <p>
                    <strong>Cause:</strong> {result.solution.Cause}
                  </p>
                  <p>
                    <strong>Peak Season:</strong>{" "}
                    {result.solution["Peak Season"]}
                  </p>
                  <p>
                    <strong>Remedy:</strong> {result.solution.Remedy}
                  </p>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <h4 className="font-medium">Confidence:</h4>
                <span className="text-sm bg-primary/10 text-primary px-2 py-1 rounded-full">
                  {result.confidence.toFixed(2)}%
                </span>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="text-sm text-muted-foreground">
          Upload a crop image to get disease identification and treatment
          recommendations
        </CardFooter>
      </Card>
    </main>
  );
}
