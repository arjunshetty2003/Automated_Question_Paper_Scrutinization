# Automated Question Paper Scrutinization

A full-stack application for automated question paper validation against syllabi and textbooks using Google Gemini AI and vector similarity search.

## Overview

This system helps educators validate question papers against syllabi and textbooks to ensure that exam questions are within the prescribed curriculum. The system uses Google Gemini AI, FAISS vector search, MongoDB, Flask, and React.

## Features

- Upload syllabus in JSON format
- Upload textbooks in PDF format
- Upload question papers in JSON format
- Validate question papers against syllabi and textbooks
- View detailed validation results with syllabus and textbook coverage analysis

## Data Formats

### Syllabus JSON Format
```json
{
  "course_name": "Operating Systems",
  "units": [
    {
      "unit_id": "UNIT-I",
      "unit_title": "Introduction to Operating Systems",
      "content": "Detailed syllabus content for Unit I..."
    }
  ]
}
```

### Question Paper JSON Format
```json
[
  {
    "question": "UNIT-I - 1",
    "text": "Explain the role of system calls in an operating system."
  }
]
``` 