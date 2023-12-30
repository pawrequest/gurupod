# #
# FROM python:3.12
#
# #
# WORKDIR /code
#
# #
# COPY ./requirements.txt /code/requirements.txt
# COPY ./pyproject.toml /code/pyproject.toml
# COPY ./README.md /code/README.md
#
# #
# COPY ./src /code/src
# COPY ./data /code/data
#
# #
# RUN pip install --no-cache-dir --upgrade pip && pip install -e .
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]


# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY requirements.txt /code/requirements.txt
COPY pyproject.toml /code/pyproject.toml
COPY README.md /code/README.md

# Copy the src and data directories
COPY src /code/src

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install -e .

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
