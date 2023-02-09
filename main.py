from fastapi import FastAPI, HTTPException,WebSocket
from pydantic import BaseModel
from typing import List, Union
from fastapi.middleware.cors import CORSMiddleware
import redis 
import json


class Item(BaseModel):
    id: int

class NewStrategy(BaseModel):
    id: int 
    name : str 

app = FastAPI()

origins = ["*"]

redisConn = redis.Redis(host='localhost', port=6379, db=0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


strategiesList = []
activeStrategiesList = []

def updateRedisData(key: str, data : any):
    redisConn.set(key, json.dumps(data))

def getRedisData(key: str):
    return json.loads(redisConn.get(key))


@app.get("/strategies")
async def strategies():
    data = getRedisData('strategiesList')
    if data != None:
        return data
    else:
        updateRedisData('strategiesList', [])
        return []    


@app.post("/addStrategy")
async def addStrategy(item : NewStrategy):
    strategiesList.insert(0, { 'id' : item.id, 'name' : item.name})

    updateRedisData('strategiesList', strategiesList)
    return strategiesList


@app.delete("/deleteStrategy")
async def deleteStrategy(id : int):
    print(id)
    index = None
    for i in range(len(strategiesList)):
        for key in strategiesList[i]:
            print(i)
            if strategiesList[i][key] == id:
                index = i
                break

    if index != None:
        print(index)
        del strategiesList[index]

    updateRedisData('strategiesList', strategiesList)
    return strategiesList

@app.get("/activeStrategies")
async def activeStrategies():
    return activeStrategiesList

@app.post("/startStrategy")
async def startStrategy(req: Item):
    for i in range(len(strategiesList)):
        for key in strategiesList[i]:
            if strategiesList[i][key] == req.id:
                activeStrategiesList.append(strategiesList[i])
                break


    return activeStrategiesList


@app.post("/stopStrategy")
async def stopStrategy(req: Item):
    index = None
    for i in range(len(activeStrategiesList)):
        for key in activeStrategiesList[i]:
            if activeStrategiesList[i][key] == req.id:
                index = i
                break

    
    if(index != None):
        del activeStrategiesList[index]

    
    return activeStrategiesList


