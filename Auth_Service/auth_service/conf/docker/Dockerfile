FROM python:3.11 AS dev_stage

# Set the working directory
WORKDIR /d_app
# Copy the requirements file into the container
COPY requirements.txt ../../../
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code into the container

RUN python manage.py collectstatic --noinput

COPY ../../ .

FROM python:3.11-slim AS prod_stage

# Set the working directory
WORKDIR /p_app

COPY --from=dev_stage /d_app /p_app

#Install python the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

ENTRYPOINT [ "" ]
CMD ["uvicorn", "main:app", "--host", "", "--port", "8000", "--reload", "--reload-dir", "/app"]