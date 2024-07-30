import javax.annotation.PreDestroy;

@Service
public class RequestServiceImpl implements RequestService {

    // Existing fields and methods

    @PreDestroy
    public void shutDown() {
        threadPoolExecutor.shutdown();
        try {
            if (!threadPoolExecutor.awaitTermination(60, TimeUnit.SECONDS)) {
                threadPoolExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            threadPoolExecutor.shutdownNow();
        }
    }
}
