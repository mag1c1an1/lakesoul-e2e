application mode

# PG

docker run -d --name lakesoul-e2e-pg -p4321:5432 -e POSTGRES_USER=lakesoul_e2e -e POSTGRES_PASSWORD=lakesoul_e2e -e POSTGRES_DB=lakesoul_e2e -d swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/postgres:14.5 

docker cp meta_init.sql lakesoul-e2e-pg:/ 

docker exec -i lakesoul-e2e-pg sh -c "PGPASSWORD=lakesoul_e2e psql -h localhost -p 5432 -U lakesoul_e2e -f meta_init.sql"

# important
pipx install is slow
