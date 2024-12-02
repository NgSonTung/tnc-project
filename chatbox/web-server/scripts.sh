#!/bin/bash

if [ "$test" = "1" ]; then
    # Run specific actions when test=1
    echo "Test mode is enabled"
    # Add your commands here
else
    # Default actions when test is not set or has a different value
    echo "Test mode is not enabled"
    # Add your default commands here
fi