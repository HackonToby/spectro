     import kopf
     import kubernetes.client as k8s_client
     from kubernetes.client.rest import ApiException
    
    # API Group : example.com type: clusterscans, version: v1, modify this part based on request
     @kopf.on.create('example.com', 'v1', 'clusterscans')
     def create_fn(spec, **kwargs):
         name = spec.get('name')
         schedule = spec.get('schedule')
         job_template = spec.get('jobTemplate')

         # Create a Kubernetes Job or CronJob based on the spec
         if schedule:
             create_cronjob(name, schedule, job_template)
         else:
             create_job(name, job_template)

     def create_job(name, job_template):
         batch_v1 = k8s_client.BatchV1Api()
         job = k8s_client.V1Job(
             api_version="batch/v1",
             kind="Job",
             metadata=k8s_client.V1ObjectMeta(name=name),
             spec=job_template
         )
         try:
             batch_v1.create_namespaced_job(namespace="default", body=job)
         except ApiException as e:
             print(f"Exception when creating job: {e}")

     def create_cronjob(name, schedule, job_template):
         batch_v1beta1 = k8s_client.BatchV1beta1Api()
         cronjob = k8s_client.V1beta1CronJob(
             api_version="batch/v1beta1",
             kind="CronJob",
             metadata=k8s_client.V1ObjectMeta(name=name),
             spec=k8s_client.V1beta1CronJobSpec(
                 schedule=schedule,
                 job_template=k8s_client.V1beta1JobTemplateSpec(
                     spec=job_template
                 )
             )
         )
         try:
             batch_v1beta1.create_namespaced_cron_job(namespace="default", body=cronjob)
         except ApiException as e:
             print(f"Exception when creating cronjob: {e}")

     if __name__ == '__main__':
         kopf.run()