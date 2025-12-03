# NYC Traffic + Weather Data Curation & Analysis Workflow

This repository contains the full workflow to reproduce the curated NYC traffic accident + weather dataset and generate analysis outputs inside a Dockerized environment.

---

#### 1. Clone the Repository and Download Dataset
* Clone the repository to your local machine and open it in VS Code
* The dataset was too large to include in the repository so visit https://catalog.data.gov/dataset/motor-vehicle-collisions-crashes 
* Scroll down to **Downloads & Resources**
* Click on Download button next to **Comma Seperated Values File** so that you can download the dataset as csv (download may take a few minutes)
* Once dataset is downloaded drag it into the repository folder in VS Code ensure that dataset is named `Motor_Vehicle_Collisions_-_Crashes.csv` and is in the `datasets` folder.


###  Docker
Download and install Docker Desktop:

- https://www.docker.com/products/docker-desktop

Follow the steps and make sure Docker is running:

```bash
docker --version
```

To run the workflow, open up a new terminal and paste the following commands.


```bash
chmod +x run_analysis.sh
```

```bash
./run_analysis.sh
```

Thats it! The script will build the Docker image, run the analysis scripts, and output the results in the `results/` directory.

If want to check the prepocessing file you can look at preprocessing.ipynb and run the cells there in a Jupyter environment. This has already been completed for the sake of time but if you want to re-run it you can do so there.