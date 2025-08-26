#!/bin/bash
echo "Starting XenToba Application with Frontend..."
echo ""
echo "Access the frontend at: http://localhost:8000"
echo "Access the API docs at: http://localhost:8000/api/v1/docs"
echo ""
uvicorn main:app --reload
