#ifndef SQLITE3_H
#define SQLITE3_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct sqlite3 sqlite3;
typedef int (*sqlite3_callback)(void*, int, char**, char**);

#define SQLITE_OK 0

int sqlite3_open(const char *filename, sqlite3 **ppDb);
int sqlite3_exec(
    sqlite3 *db,
    const char *sql,
    sqlite3_callback callback,
    void *arg,
    char **errmsg
);
int sqlite3_close(sqlite3 *db);
const char *sqlite3_errmsg(sqlite3 *db);
void sqlite3_free(void *ptr);

#ifdef __cplusplus
}
#endif

#endif // SQLITE3_H
