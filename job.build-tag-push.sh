docker buildx build --platform linux/amd64 -t oci-utility-job:latest .
docker tag oci-utility-job:latest <region name>/<tenancy name>/oci-utility-job:latest
docker push <region name>/<tenancy name>/oci-utility-job:latest
