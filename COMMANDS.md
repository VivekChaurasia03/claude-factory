# Commands History

Commands given during learning sessions. Copy from here to avoid formatting issues.

---

## Chunk 1.2 — Kafka Setup

### Start Kafka container (apache/kafka 3.7.2)
```
docker run -d --name kafka -p 9092:9092 -e KAFKA_NODE_ID=1 -e KAFKA_PROCESS_ROLES=broker,controller -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e KAFKA_AUTO_CREATE_TOPICS_ENABLE=true apache/kafka:3.7.2
```

### Start Kafka UI (web dashboard on http://localhost:8080)
```
docker run -d --name kafka-ui -p 8080:8080 -e KAFKA_CLUSTERS_0_NAME=windborne -e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=host.docker.internal:9092 provectuslabs/kafka-ui:latest
```

### Verify Kafka is running
```
docker ps
```

### Stop and remove Kafka container
```
docker rm -f kafka
```

### Stop and remove both Kafka and Kafka UI
```
docker rm -f kafka kafka-ui
```

### Start Kafka with host.docker.internal advertised listener (fixes Kafka UI connectivity)
```
docker run -d --name kafka -p 9092:9092 -e KAFKA_NODE_ID=1 -e KAFKA_PROCESS_ROLES=broker,controller -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://host.docker.internal:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e KAFKA_AUTO_CREATE_TOPICS_ENABLE=true apache/kafka:3.7.2
```

Resume this session with:
claude --resume "[VC - Windbore_UpSkill]" 