# DSP-TOOLS Exception System - Flow Diagrams

## 1. Exception Propagation and Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Command Execution                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Function raises  │
                    │  specific error  │
                    │ (e.g., InputError)
                    └─────────┬────────┘
                              │
                              ▼
                 ┌────────────────────────────┐
                 │ Propagates up call stack   │
                 │ (unless caught locally)    │
                 └────────────┬───────────────┘
                              │
                              ▼
                 ┌────────────────────────────┐
                 │  CLI entry_point.py catches│
                 │     exception as           │
                 │     BaseError or Exception │
                 └────────────┬───────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
         ┌──────────────┐         ┌──────────────────┐
         │ BaseError    │         │ Generic Exception│
         │    caught    │         │      caught      │
         └──────┬───────┘         └────────┬─────────┘
                │                          │
                ▼                          ▼
    ┌────────────────────┐      ┌──────────────────┐
    │ logger.exception() │      │ print(          │
    │ log to file        │      │  InternalError())│
    │                    │      │ Requests dev help│
    └────────────────────┘      └──────────────────┘
                │                          │
                ▼                          ▼
    ┌────────────────────┐      ┌──────────────────┐
    │ print BOLD_RED     │      │ logger.exception()│
    │ error message      │      │ log to file       │
    │ to stdout          │      └──────────────────┘
    └────────┬───────────┘               │
             │                           ▼
             └─────────────┬──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  sys.exit(1) │
                   │  Error code  │
                   └──────────────┘
```

---

## 2. Exception Type Selection by Scenario

```
┌─────────────────────────────────────────────────────────────────┐
│                  Error Occurs in Code                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌───────────┐  ┌──────────┐  ┌──────────┐
        │ User's    │  │ System/  │  │ Domain-  │
        │ Fault?    │  │ Internal?│  │ Specific?│
        │           │  │          │  │          │
        └─────┬─────┘  └────┬─────┘  └────┬─────┘
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │InputError│  │InternalErr│ │ Specific │
        │          │  │or         │  │Error     │
        │or subclass  └──────────┘  │(XmlUp-   │
        │- UserFile-            │loadError,   │
        │  PathNotFound         │ShaclVal...  │
        │- UserDir...Found      └──────────┘
        │- JSONFileParser...  
        └──────────┘
```

---

## 3. Input Validation Exception Flow

```
CLI Input
   │
   ▼
┌──────────────────────────────────────┐
│ Check file/directory paths           │
│ (cli/utils.py)                       │
└──────────┬───────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
  Exists?      Is Dir?
    │             │
    N             N
    │             │
    ▼             ▼
┌────────────────────┐    ┌────────────────────┐
│UserFilepathNotFound│    │UserDirectoryNotFound│
│Error               │    │Error                │
└────────┬───────────┘    └────────┬───────────┘
         │                         │
         └────────┬────────────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Check Docker     │
         │ (if needed)      │
         └────────┬─────────┘
                  │
          ┌───────┴────────┐
          │                │
         NOT OK           OK
          │                │
          ▼                ▼
┌──────────────────┐   Continue
│Docker Not        │
│Reachable Error   │
└──────────────────┘
```

---

## 4. Network Request Error Handling

```
Client makes HTTP request
   │
   ▼
┌──────────────────────────┐
│ RequestException thrown? │
└───┬──────────────────────┘
    │
    YES
    │
    ▼
┌──────────────────────────┐
│ Determine error type     │
└───┬──────────────────────┘
    │
    ├─────────────────────────┐
    │                         │
    ▼                         ▼
┌────────────┐         ┌──────────────┐
│ Timeout?   │         │ Status Code? │
└───┬────────┘         └──────┬───────┘
    │                         │
    YES                   ┌───┼───┬──┐
    │                     │   │   │  │
    ▼                     5XX 4XX Retry?
┌──────────────┐          │   │   │
│Permanent     │          ▼   ▼   │
│TimeOut Error │      ┌────────┐  ▼
└──────────────┘      │Perm    │  Retry
                      │Conn Err│  Logic
                      └────────┘
```

---

## 5. Problem Collection vs Exception Pattern

```
Traditional Exception Pattern:
┌──────────────────┐
│ Validate item 1  │
└────────┬─────────┘
         │
    ┌────┴─────┐
    │           │
  Valid      Invalid
    │           │
    │           ▼
    │      ┌─────────────────┐
    │      │ Raise Exception │
    │      │ Stop processing │
    │      └─────────────────┘
    │
    ▼
 (next item never checked)


Problem Collection Pattern:
┌──────────────────┐
│ Validate item 1  │
└────────┬─────────┘
         │
    ┌────┴──────┐
    │            │
  Valid      Invalid
    │            │
    ▼            ▼
 Continue    Add to problems
    │            │
    ▼            ▼
┌──────────────────────┐
│ Validate item 2      │
└────────┬─────────────┘
         │
    ┌────┴──────┐
    │            │
  Valid      Invalid
    │            │
    ▼            ▼
 Continue    Add to problems
    │            │
    └────┬───────┘
         │
         ▼
    ┌──────────────────────┐
    │ Format all problems  │
    │ together for display │
    └────────┬─────────────┘
             │
             ▼
    ┌──────────────────────┐
    │ Show user all at once│
    └──────────────────────┘
```

---

## 6. Exception Creation and Consumption Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Exception Definition                          │
│              /src/dsp_tools/error/exceptions.py                 │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ├─── BaseError (base dataclass)
           │        │
           │        ├─ InternalError
           │        ├─ InputError (and subclasses)
           │        ├─ PermanentConnectionError → BadCredentialsError
           │        ├─ XmlUploadError → XmlUploadInterruptedError
           │        └─ ... (other 20+ exceptions)
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│          Exception Raising (69 files across codebase)           │
│                                                                 │
│  Clients → raise BadCredentialsError("invalid credentials")    │
│  CLI      → raise UserFilepathNotFoundError(file)              │
│  Commands → raise XmlUploadError("upload failed")              │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│        Exception Propagation (up call stack)                    │
│                                                                 │
│  Command function                                              │
│    └─ Helper function                                          │
│         └─ API client                                          │
│              └─ Connection                                     │
│                   └─ raise BadCredentialsError                │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│      Exception Catching (30 files across codebase)              │
│                                                                 │
│  try:                                                          │
│      call_requested_action()  ← could raise any BaseError     │
│  except BaseError as err:                                     │
│      handle user-friendly way                                 │
│  except Exception:                                            │
│      handle unexpected errors with InternalError()            │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│      Error Message Formatting and Display                       │
│                                                                 │
│  logger.exception("Error: {err.message}")  ← to file           │
│  print(BOLD_RED + f"Error: {err.message}") ← to stdout         │
│  sys.exit(1)                              ← exit code          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Exception Type Decision Tree

```
                    Error Condition
                           │
                    ┌──────┴──────┐
                    │             │
              File/Path      Everything
              Operations     Else
                    │             │
                    ▼             ▼
        ┌────────────────────┐ ┌──────────┐
        │ File/Dir Ops       │ │ What     │
        │                    │ │ failed?  │
        └──────┬─────────────┘ └────┬─────┘
               │                    │
               ▼                    │
     ┌──────────────────┐           │
     │ File exists?     │           │
     └────┬─────────────┘           │
          │                         │
      NO  │  YES                    │
      │   │                         │
      ▼   ▼                         │
  ┌──────────┐ Continue        ┌────┴──────────┬──────┬────────┬───┐
  │UserFile  │ Validation    │  │    │  │    │
  │PathNotFd │         Docker API XML User Invalid
  │Error     │                │  │    │  │    │
  └──────────┘                ▼  ▼    ▼  ▼    ▼
                         ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐
                         │Dr│ │Ds│ │Xm│ │In│ │In│
                         │Nf│ │Af│ │Up│ │Er│ │pE│
                         │Ef│ │Nf│ │Ef│ │rr│ │Er│
                         └──┘ └──┘ └──┘ └──┘ └──┘
```

---

## 8. Exception Message Flow for User

```
INTERNAL CODE EXECUTION:
═════════════════════════════════════════════════════════════

raise InputError("The provided filepath does not exist: /tmp/foo.json")
        │
        ├─ Stored in exception object
        └─ Propagates up through call stack
                  │
                  ▼
        Caught in entry_point.py


USER-FACING OUTPUT:
═════════════════════════════════════════════════════════════

LOG FILE (~/.dsp-tools/logs/):
─────────────────────────────
2024-10-29 14:32:15 | ERROR | The process was terminated because 
                       of an Error: The provided filepath does not 
                       exist: /tmp/foo.json
2024-10-29 14:32:15 | Traceback (most recent call last):
                     |   File "entry_point.py", line 72, ...
                     |   ...
                     | InputError: The provided filepath does not 
                     |   exist: /tmp/foo.json


STDOUT (Terminal):
──────────────────
[BOLD_RED]
The process was terminated because of an Error: The provided 
filepath does not exist: /tmp/foo.json
[RESET_TO_DEFAULT]


EXIT CODE: 1
```

---

## 9. Exception Conversion Pattern Example

```
Low-Level Exception:
┌──────────────────────────────┐
│ requests.RequestException    │
│ thrown by HTTP library       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Catch in connection_live.py  │
│                              │
│ except RequestException:     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Analyze and Decide Type      │
│                              │
│ if status_code >= 500:       │
│   → PermanentConnectionError │
│ elif status_code == 422:     │
│   → InvalidInputError        │
│ else:                        │
│   → PermanentConnectionError │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Mid-Level Exception Raised   │
│                              │
│ raise PermanentConnectionErr │
│ (msg) from None              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Catch in auth_client_live.py │
│                              │
│ except PermanentConnectionErr:
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Convert to User-Friendly     │
│                              │
│ raise InputError(e.message)  │
│ from None                    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ High-Level Exception Used    │
│ (final user message)         │
│                              │
│ InputError for display       │
└──────────────────────────────┘
```

---

## 10. Exception Inheritance Relationships

```
Exception (Python built-in)
│
└─ BaseError
   ├─ InternalError
   ├─ DockerNotReachableError
   ├─ DspApiNotReachableError
   ├─ InputError
   │  ├─ UserFilepathNotFoundError
   │  ├─ UserDirectoryNotFoundError
   │  ├─ JSONFileParsingError
   │  └─ DuplicateIdsInXmlAndId2IriMapping
   ├─ InvalidGuiAttributeError
   ├─ UnexpectedApiResponseError
   ├─ PermanentConnectionError
   │  └─ BadCredentialsError
   ├─ InvalidInputError
   │  └─ InvalidIngestFileNameError
   ├─ ShaclValidationCliError
   ├─ ShaclValidationError
   ├─ PermanentTimeOutError
   ├─ XmlUploadError
   │  └─ XmlUploadInterruptedError
   ├─ XmlInputConversionError
   ├─ Id2IriReplacementError
   ├─ XmlUploadPermissionsNotFoundError
   ├─ XmlUploadAuthorshipsNotFoundError
   ├─ XmlUploadListNodeNotFoundError
   ├─ UnknownDOAPException
   ├─ XmllibInputError
   ├─ XmllibFileNotFoundError
   └─ XmllibInternalError
```

---

