package com.infy.ceh.management.service;

import com.infy.ceh.management.domain.Request;
import com.infy.ceh.management.repository.RequestRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

@Service
public class RequestServiceImpl implements RequestService {

    private static final int QUEUE_CAPACITY = 10000;

    private BlockingQueue<Request> requestQueue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);

    @Autowired
    private RequestRepository requestRepository;

    @Autowired
    private ThreadPoolExecutor threadPoolExecutor;

    @Override
    public void receiveRequest(Request request) {
        try {
            requestQueue.put(request);
            threadPoolExecutor.execute(this::processRequest);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Failed to queue the request", e);
        }
    }

    public void processRequest() {
        Request request = requestQueue.poll();
        if (request != null) {
            try {
                requestRepository.saveRequest(request);
            } catch (Exception e) {
                // Handle failed processing (e.g., log, retry, move to a dead-letter queue)
            }
        }
    }
}
