cmake_minimum_required(VERSION 2.8.9)
include(${SCRIPT_DIR}/CMakeAll.txt)

project("scripts_rj")
message("Project name   : ${PROJECT_NAME}")
message("Project include: ${PROJECT_SOURCE_DIR}")

set(libname "scripts")

set( PY_CODE
    backup.py
    replace.py
)

source_group( "script" FILES ${PY_CODE} )


install( PROGRAMS ${PY_CODE} DESTINATION ${inst_bin_dir})


############################################################################### 

set(ENV{SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR} )
set(ENV{DOC_DIR}    ${inst_doc_dir}/${libname} )

message("Source dir: $ENV{SOURCE_DIR} " )
message("Doc    dir: $ENV{DOC_DIR} " )

add_custom_target(doc
    COMMAND ${SCRIPT_DIR}/doxigen_stup ${DOXYGEN_EXECUTABLE}  ${CMAKE_CURRENT_SOURCE_DIR}/doxygen.dox $ENV{SOURCE_DIR} $ENV{DOC_DIR}
    #export SOURCE_DIR=$ENV{SOURCE_DIR};export DOC_DIR=$ENV{DOC_DIR};${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/doxygen.dox 
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating API documentation" VERBATIN
)

###############################################################################

