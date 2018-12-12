pipeline {
    agent {
        kubernetes {
            label 'python-stretch'
        }
    }
    stages {
        stage('Prepare') {
            steps {
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                }
                container('vault') {
                    script {
                        env.PYPI_USERNAME = sh(script: 'vault read -field=username secret/ops/account/pypi', returnStdout: true)
                        env.PYPI_PASSWORD = sh(script: 'vault read -field=password secret/ops/account/pypi', returnStdout: true)
                        env.PYPI_LOCAL_USERNAME = sh(script: 'vault read -field=username secret/ops/account/nexus', returnStdout: true)
                        env.PYPI_LOCAL_PASSWORD = sh(script: 'vault read -field=password secret/ops/account/nexus', returnStdout: true)
                        env.GITHUB_TOKEN = sh(script: 'vault read -field=value secret/ops/token/github', returnStdout: true)
                    }
                }
                container('python') {
                    script {
                        sh "pip install bumpversion"
                        sh "pip install twine"
                    }
                }
            }
        }
        stage('Build: [ pull request ]') {
            when {
                changeRequest()
            }
            steps {
                container('python') {
                    sh "pip install ."
                    sh "python -m unittest discover . '*_test.py'"
                }
            }
        }
        stage('Build: [ master ]') {
            when {
                branch 'master'
            }
            steps {
                milestone 1
                container('node') {
                    sh "pip install ."
                    sh "python -m unittest discover . '*_test.py'"
                }
            }
        }
        stage('Release: [ master ]') {
            when {
                branch 'master'
            }
            environment {
                REPOSITORY = 'molgenis/molgenis-tools-mdev'
            }
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        env.RELEASE_SCOPE = input(
                                message: 'Do you want to release?',
                                ok: 'Release',
                                parameters: [
                                        choice(choices: 'patch\nminor\nmajor', description: '', name: 'RELEASE_SCOPE')
                                ]
                        )
                    }
                }
                milestone 2
                container('python') {
                    sh "git remote set-url origin https://${GITHUB_TOKEN}@github.com/${REPOSITORY}.git"

                    sh "git checkout -f ${BRANCH_NAME}"

                    sh "bumpversion ${RELEASE_SCOPE} setup.py"

//                    sh "git push --tags origin master"

                    sh "twine upload -r ${PYPI_LOCAL_REGISTRY} -u ${PYPI_LOCAL_USERNAME} -p ${PYPI_LOCAL_PASSWORD} dist/*"
                    hubotSend(message: '${env.REPOSITORY} has been successfully deployed on ${env.PYPI_LOCAL_REGISTRY}.', status:'SUCCESS')
                }
            }
        }
    }
    post{
        success {
            notifySuccess()
        }
        failure {
            notifyFailed()
        }
    }
}

def notifySuccess() {
    hubotSend(message: 'Build success', status:'INFO', site: 'slack-pr-app-team')
}

def notifyFailed() {
    hubotSend(message: 'Build failed', status:'ERROR', site: 'slack-pr-app-team')
}